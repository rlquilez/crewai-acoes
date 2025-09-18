"""
Integração MCP (Model Context Protocol) para Alpha Vantage.
Implementa acesso direto aos dados do Alpha Vantage via MCP conforme 
documentado em https://mcp.alphavantage.co/
"""

import os
import json
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import aiohttp

logger = logging.getLogger(__name__)

# Importação opcional do MCP
try:
    import mcp
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    logger.warning("MCP (Model Context Protocol) não está disponível. Instale com: pip install mcp")

@dataclass
class MCPConfig:
    """Configuração para MCP Alpha Vantage"""
    api_key: str
    enabled: bool = False
    base_url: str = "https://mcp.alphavantage.co"
    timeout: int = 30
    max_retries: int = 3

class AlphaVantageMCPClient:
    """Cliente MCP para Alpha Vantage"""
    
    def __init__(self):
        self.config = self._load_config()
        self._session: Optional[aiohttp.ClientSession] = None
    
    def _load_config(self) -> MCPConfig:
        """Carrega configuração MCP"""
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        enabled = os.getenv('ALPHA_VANTAGE_MCP_ENABLED', 'true').lower() == 'true'
        
        return MCPConfig(
            api_key=api_key or "",
            enabled=enabled and bool(api_key),
            timeout=int(os.getenv('ALPHA_VANTAGE_MCP_TIMEOUT', '30')),
            max_retries=int(os.getenv('ALPHA_VANTAGE_MCP_RETRIES', '3'))
        )
    
    def is_available(self) -> bool:
        """Verifica se MCP está disponível"""
        return MCP_AVAILABLE and self.config.enabled and bool(self.config.api_key)
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Obtém sessão HTTP reutilizável"""
        if self._session is None or self._session.closed:
            headers = {
                'Authorization': f'Bearer {self.config.api_key}',
                'Content-Type': 'application/json',
                'User-Agent': 'CrewAI-Stock-Analysis/2.0'
            }
            
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            self._session = aiohttp.ClientSession(
                headers=headers,
                timeout=timeout,
                connector=aiohttp.TCPConnector(limit=10)
            )
        
        return self._session
    
    async def close(self):
        """Fecha conexões"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def _make_mcp_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Faz requisição MCP formatada"""
        if not self.is_available():
            raise ValueError("Alpha Vantage MCP não está configurado")
        
        session = await self._get_session()
        
        # Formato padrão MCP
        mcp_request = {
            "jsonrpc": "2.0",
            "id": f"alphavantage_{method}_{hash(str(params))}",
            "method": method,
            "params": {
                "apikey": self.config.api_key,
                **params
            }
        }
        
        for attempt in range(self.config.max_retries):
            try:
                async with session.post(
                    f"{self.config.base_url}/v1/mcp",
                    json=mcp_request
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    # Verifica erro MCP
                    if 'error' in data:
                        raise ValueError(f"MCP Error: {data['error']}")
                    
                    return data.get('result', {})
                    
            except aiohttp.ClientError as e:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}")
                if attempt == self.config.max_retries - 1:
                    raise
                await asyncio.sleep(2 ** attempt)  # Backoff exponencial
        
        raise RuntimeError("Falha após todas as tentativas")
    
    async def get_company_overview_mcp(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém visão geral da empresa via MCP"""
        try:
            result = await self._make_mcp_request(
                "company_overview",
                {"symbol": symbol}
            )
            
            if not result:
                return None
            
            # Estrutura os dados no formato esperado
            return {
                'symbol': result.get('Symbol'),
                'name': result.get('Name'),
                'description': result.get('Description'),
                'sector': result.get('Sector'),
                'industry': result.get('Industry'),
                'market_cap': result.get('MarketCapitalization'),
                'pe_ratio': result.get('PERatio'),
                'peg_ratio': result.get('PEGRatio'),
                'price_to_book': result.get('PriceToBookRatio'),
                'ev_to_ebitda': result.get('EVToEBITDA'),
                'roe': result.get('ReturnOnEquityTTM'),
                'roa': result.get('ReturnOnAssetsTTM'),
                'profit_margin': result.get('ProfitMargin'),
                'operating_margin': result.get('OperatingMarginTTM'),
                'revenue_ttm': result.get('RevenueTTM'),
                'ebitda': result.get('EBITDA'),
                'eps': result.get('EPS'),
                'dividend_yield': result.get('DividendYield'),
                'beta': result.get('Beta'),
                '52_week_high': result.get('52WeekHigh'),
                '52_week_low': result.get('52WeekLow'),
                'analyst_target_price': result.get('AnalystTargetPrice'),
                'mcp_source': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter company overview via MCP para {symbol}: {e}")
            return None
    
    async def get_financial_statements_mcp(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém demonstrações financeiras via MCP"""
        try:
            # Busca múltiplas demonstrações em paralelo
            tasks = [
                self._make_mcp_request("income_statement", {"symbol": symbol}),
                self._make_mcp_request("balance_sheet", {"symbol": symbol}),
                self._make_mcp_request("cash_flow", {"symbol": symbol}),
                self._make_mcp_request("earnings", {"symbol": symbol})
            ]
            
            income, balance, cash_flow, earnings = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            result = {
                'symbol': symbol,
                'mcp_source': True,
                'timestamp': str(asyncio.get_event_loop().time())
            }
            
            # Adiciona dados se não houve erro
            if not isinstance(income, Exception) and income:
                result['income_statement'] = income
            
            if not isinstance(balance, Exception) and balance:
                result['balance_sheet'] = balance
            
            if not isinstance(cash_flow, Exception) and cash_flow:
                result['cash_flow'] = cash_flow
            
            if not isinstance(earnings, Exception) and earnings:
                result['earnings'] = earnings
            
            return result if len(result) > 3 else None  # Pelo menos um resultado além dos metadados
            
        except Exception as e:
            logger.error(f"Erro ao obter demonstrações financeiras via MCP para {symbol}: {e}")
            return None
    
    async def get_time_series_mcp(self, symbol: str, function: str = "TIME_SERIES_DAILY") -> Optional[Dict[str, Any]]:
        """Obtém séries temporais via MCP"""
        try:
            result = await self._make_mcp_request(
                "time_series",
                {
                    "symbol": symbol,
                    "function": function,
                    "outputsize": "compact"
                }
            )
            
            if not result:
                return None
            
            return {
                'symbol': symbol,
                'function': function,
                'time_series_data': result,
                'mcp_source': True
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter time series via MCP para {symbol}: {e}")
            return None
    
    async def get_comprehensive_data_mcp(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados abrangentes via MCP (overview + financials + time series)
        """
        if not self.is_available():
            return {'mcp_available': False}
        
        logger.info(f"Coletando dados abrangentes via MCP para {symbol}")
        
        try:
            # Executa buscas em paralelo
            tasks = [
                self.get_company_overview_mcp(symbol),
                self.get_financial_statements_mcp(symbol),
                self.get_time_series_mcp(symbol)
            ]
            
            overview, financials, time_series = await asyncio.gather(
                *tasks, return_exceptions=True
            )
            
            result = {
                'symbol': symbol,
                'mcp_available': True,
                'mcp_source': True,
                'data_sources': []
            }
            
            # Adiciona dados coletados
            if not isinstance(overview, Exception) and overview:
                result['company_overview'] = overview
                result['data_sources'].append('company_overview')
            
            if not isinstance(financials, Exception) and financials:
                result['financial_statements'] = financials
                result['data_sources'].append('financial_statements')
            
            if not isinstance(time_series, Exception) and time_series:
                result['time_series'] = time_series
                result['data_sources'].append('time_series')
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter dados abrangentes via MCP para {symbol}: {e}")
            return {'mcp_available': False, 'error': str(e)}
        finally:
            await self.close()
    
    def get_mcp_context_structured(self, symbol: str, data: Dict[str, Any]) -> str:
        """
        Gera contexto estruturado otimizado para LLMs baseado nos dados MCP
        """
        if not data.get('mcp_source'):
            return ""
        
        context_parts = [
            f"=== ALPHA VANTAGE MCP DATA FOR {symbol} ===",
            "Source: Alpha Vantage via Model Context Protocol",
            "Documentation: https://mcp.alphavantage.co/",
            ""
        ]
        
        # Company Overview
        if 'company_overview' in data:
            overview = data['company_overview']
            context_parts.extend([
                "COMPANY FUNDAMENTALS (MCP):",
                f"• Company: {overview.get('name', 'N/A')}",
                f"• Sector: {overview.get('sector', 'N/A')}",
                f"• Industry: {overview.get('industry', 'N/A')}",
                f"• Market Cap: {overview.get('market_cap', 'N/A')}",
                f"• P/E Ratio: {overview.get('pe_ratio', 'N/A')}",
                f"• PEG Ratio: {overview.get('peg_ratio', 'N/A')}",
                f"• ROE: {overview.get('roe', 'N/A')}",
                f"• Profit Margin: {overview.get('profit_margin', 'N/A')}",
                f"• EPS: {overview.get('eps', 'N/A')}",
                f"• Dividend Yield: {overview.get('dividend_yield', 'N/A')}",
                ""
            ])
        
        # Financial Statements
        if 'financial_statements' in data:
            context_parts.extend([
                "FINANCIAL STATEMENTS (MCP):",
                "• Income Statement: Available",
                "• Balance Sheet: Available", 
                "• Cash Flow: Available",
                "• Earnings History: Available",
                ""
            ])
        
        # Time Series
        if 'time_series' in data:
            context_parts.extend([
                "PRICE DATA (MCP):",
                "• Daily time series available",
                "• Historical price data included",
                ""
            ])
        
        context_parts.extend([
            "MCP ADVANTAGES:",
            "• Real-time structured data",
            "• Standardized format",
            "• Enhanced accuracy",
            "• Optimized for AI analysis"
        ])
        
        return "\n".join(context_parts)

# Instância global do cliente MCP
mcp_client = AlphaVantageMCPClient()

# Funções síncronas para compatibilidade
def get_alpha_vantage_mcp_data(symbol: str) -> Dict[str, Any]:
    """Função síncrona para obter dados MCP"""
    if not mcp_client.is_available():
        return {'mcp_available': False}
    
    # Executa de forma síncrona
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    return loop.run_until_complete(mcp_client.get_comprehensive_data_mcp(symbol))

def is_mcp_available() -> bool:
    """Verifica se MCP está disponível"""
    return mcp_client.is_available()

def get_mcp_context(symbol: str, data: Dict[str, Any]) -> str:
    """Gera contexto MCP estruturado"""
    return mcp_client.get_mcp_context_structured(symbol, data)
