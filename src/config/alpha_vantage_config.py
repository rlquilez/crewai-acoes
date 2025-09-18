"""
Sistema de configuração e integração com Alpha Vantage para dados financeiros.
Trabalha em conjunto com Yahoo Finance para dados mais completos.
Inclui suporte para MCP (Model Context Protocol) conforme documentado em https://mcp.alphavantage.co/
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@dataclass
class AlphaVantageConfig:
    """Configuração para Alpha Vantage"""
    api_key: str
    enabled: bool = False
    premium: bool = False
    timeout: int = 30
    base_url: str = "https://www.alphavantage.co/query"
    mcp_enabled: bool = False

class AlphaVantageManager:
    """Gerenciador de integração com Alpha Vantage"""
    
    def __init__(self):
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> AlphaVantageConfig:
        """Carrega configuração do Alpha Vantage"""
        api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
        enabled = os.getenv('ALPHA_VANTAGE_ENABLED', 'false').lower() == 'true'
        premium = os.getenv('ALPHA_VANTAGE_PREMIUM', 'false').lower() == 'true'
        timeout = int(os.getenv('ALPHA_VANTAGE_TIMEOUT', '30'))
        
        return AlphaVantageConfig(
            api_key=api_key or "",
            enabled=enabled and bool(api_key),
            premium=premium,
            timeout=timeout,
            mcp_enabled=bool(api_key)  # MCP disponível se API key configurada
        )
    
    def _validate_config(self):
        """Valida configuração do Alpha Vantage"""
        if self.config.enabled and not self.config.api_key:
            logger.warning("Alpha Vantage habilitado mas API key não configurada")
            self.config.enabled = False
        
        if self.config.enabled:
            logger.info("Alpha Vantage configurado e habilitado")
        else:
            logger.info("Alpha Vantage não configurado ou desabilitado")
    
    def is_available(self) -> bool:
        """Verifica se Alpha Vantage está disponível"""
        return self.config.enabled and bool(self.config.api_key)
    
    def _make_request(self, function: str, symbol: str = None, **params) -> Dict[str, Any]:
        """Faz requisição para Alpha Vantage API"""
        if not self.is_available():
            raise ValueError("Alpha Vantage não está configurado ou habilitado")
        
        request_params = {
            'function': function,
            'apikey': self.config.api_key,
            **params
        }
        
        if symbol:
            request_params['symbol'] = symbol
        
        try:
            response = requests.get(
                self.config.base_url,
                params=request_params,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Verifica se há erro na resposta
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage Error: {data['Error Message']}")
            
            if 'Note' in data:
                logger.warning(f"Alpha Vantage Note: {data['Note']}")
            
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para Alpha Vantage: {e}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar resposta JSON: {e}")
            raise
    
    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém visão geral da empresa (dados fundamentalistas)"""
        if not self.is_available():
            return None
        
        try:
            data = self._make_request('OVERVIEW', symbol=symbol)
            
            if not data or 'Symbol' not in data:
                return None
            
            return {
                'symbol': data.get('Symbol'),
                'name': data.get('Name'),
                'description': data.get('Description'),
                'sector': data.get('Sector'),
                'industry': data.get('Industry'),
                'market_cap': data.get('MarketCapitalization'),
                'pe_ratio': data.get('PERatio'),
                'peg_ratio': data.get('PEGRatio'),
                'price_to_book': data.get('PriceToBookRatio'),
                'ev_to_ebitda': data.get('EVToEBITDA'),
                'roe': data.get('ReturnOnEquityTTM'),
                'roa': data.get('ReturnOnAssetsTTM'),
                'profit_margin': data.get('ProfitMargin'),
                'operating_margin': data.get('OperatingMarginTTM'),
                'revenue_ttm': data.get('RevenueTTM'),
                'gross_profit_ttm': data.get('GrossProfitTTM'),
                'ebitda': data.get('EBITDA'),
                'eps': data.get('EPS'),
                'dividend_yield': data.get('DividendYield'),
                'beta': data.get('Beta'),
                '52_week_high': data.get('52WeekHigh'),
                '52_week_low': data.get('52WeekLow'),
                'analyst_target_price': data.get('AnalystTargetPrice'),
                'book_value': data.get('BookValue')
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter overview da empresa {symbol}: {e}")
            return None
    
    def get_earnings(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de earnings (resultados trimestrais)"""
        if not self.is_available():
            return None
        
        try:
            data = self._make_request('EARNINGS', symbol=symbol)
            
            if not data or 'symbol' not in data:
                return None
            
            return {
                'symbol': data.get('symbol'),
                'annual_earnings': data.get('annualEarnings', []),
                'quarterly_earnings': data.get('quarterlyEarnings', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter earnings de {symbol}: {e}")
            return None
    
    def get_cash_flow(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém dados de fluxo de caixa"""
        if not self.is_available():
            return None
        
        try:
            data = self._make_request('CASH_FLOW', symbol=symbol)
            
            if not data or 'symbol' not in data:
                return None
            
            return {
                'symbol': data.get('symbol'),
                'annual_reports': data.get('annualReports', []),
                'quarterly_reports': data.get('quarterlyReports', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter cash flow de {symbol}: {e}")
            return None
    
    def get_income_statement(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém demonstração de resultados"""
        if not self.is_available():
            return None
        
        try:
            data = self._make_request('INCOME_STATEMENT', symbol=symbol)
            
            if not data or 'symbol' not in data:
                return None
            
            return {
                'symbol': data.get('symbol'),
                'annual_reports': data.get('annualReports', []),
                'quarterly_reports': data.get('quarterlyReports', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter income statement de {symbol}: {e}")
            return None
    
    def get_balance_sheet(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Obtém balanço patrimonial"""
        if not self.is_available():
            return None
        
        try:
            data = self._make_request('BALANCE_SHEET', symbol=symbol)
            
            if not data or 'symbol' not in data:
                return None
            
            return {
                'symbol': data.get('symbol'),
                'annual_reports': data.get('annualReports', []),
                'quarterly_reports': data.get('quarterlyReports', [])
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter balance sheet de {symbol}: {e}")
            return None
    
    def get_enhanced_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados financeiros completos combinando múltiplas funções.
        Usado como complemento aos dados do Yahoo Finance.
        """
        if not self.is_available():
            return {'alpha_vantage_available': False}
        
        logger.info(f"Coletando dados financeiros aprimorados para {symbol} via Alpha Vantage")
        
        enhanced_data = {
            'alpha_vantage_available': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat()
        }
        
        # Coleta dados fundamentalistas
        overview = self.get_company_overview(symbol)
        if overview:
            enhanced_data['company_overview'] = overview
        
        # Coleta earnings
        earnings = self.get_earnings(symbol)
        if earnings:
            enhanced_data['earnings'] = earnings
        
        # Para contas premium, coleta dados adicionais
        if self.config.premium:
            cash_flow = self.get_cash_flow(symbol)
            if cash_flow:
                enhanced_data['cash_flow'] = cash_flow
            
            income_statement = self.get_income_statement(symbol)
            if income_statement:
                enhanced_data['income_statement'] = income_statement
            
            balance_sheet = self.get_balance_sheet(symbol)
            if balance_sheet:
                enhanced_data['balance_sheet'] = balance_sheet
        
        return enhanced_data
    
    def get_mcp_context(self, symbol: str) -> str:
        """
        Gera contexto estruturado para MCP (Model Context Protocol)
        Conforme documentação em https://mcp.alphavantage.co/
        """
        if not self.config.mcp_enabled:
            return ""
        
        try:
            data = self.get_enhanced_financial_data(symbol)
            
            if not data.get('alpha_vantage_available'):
                return ""
            
            # Estrutura o contexto para MCP
            context_parts = [
                f"=== ALPHA VANTAGE ENHANCED DATA FOR {symbol} ===",
                f"Data Source: Alpha Vantage API",
                f"Timestamp: {data.get('timestamp')}",
                ""
            ]
            
            # Company Overview
            if 'company_overview' in data:
                overview = data['company_overview']
                context_parts.extend([
                    "COMPANY OVERVIEW:",
                    f"Name: {overview.get('name', 'N/A')}",
                    f"Sector: {overview.get('sector', 'N/A')}",
                    f"Industry: {overview.get('industry', 'N/A')}",
                    f"Market Cap: {overview.get('market_cap', 'N/A')}",
                    f"P/E Ratio: {overview.get('pe_ratio', 'N/A')}",
                    f"PEG Ratio: {overview.get('peg_ratio', 'N/A')}",
                    f"Price to Book: {overview.get('price_to_book', 'N/A')}",
                    f"ROE: {overview.get('roe', 'N/A')}",
                    f"ROA: {overview.get('roa', 'N/A')}",
                    f"Profit Margin: {overview.get('profit_margin', 'N/A')}",
                    f"EPS: {overview.get('eps', 'N/A')}",
                    f"Beta: {overview.get('beta', 'N/A')}",
                    ""
                ])
            
            # Earnings Summary
            if 'earnings' in data:
                earnings = data['earnings']
                context_parts.extend([
                    "RECENT EARNINGS:",
                    f"Latest quarterly earnings available",
                    f"Annual earnings data available",
                    ""
                ])
            
            # Premium data if available
            if self.config.premium:
                context_parts.extend([
                    "PREMIUM DATA AVAILABLE:",
                    "- Cash Flow Statements",
                    "- Income Statements", 
                    "- Balance Sheets",
                    ""
                ])
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Erro ao gerar contexto MCP para {symbol}: {e}")
            return ""

# Instância global do gerenciador
alpha_vantage_manager = AlphaVantageManager()

def get_alpha_vantage_data(symbol: str) -> Dict[str, Any]:
    """Função de conveniência para obter dados do Alpha Vantage"""
    return alpha_vantage_manager.get_enhanced_financial_data(symbol)

def is_alpha_vantage_available() -> bool:
    """Verifica se Alpha Vantage está disponível"""
    return alpha_vantage_manager.is_available()

def get_alpha_vantage_mcp_context(symbol: str) -> str:
    """Obtém contexto MCP do Alpha Vantage"""
    return alpha_vantage_manager.get_mcp_context(symbol)
