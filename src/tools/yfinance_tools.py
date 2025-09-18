"""
Ferramentas para obter dados financeiros usando Yahoo Finance e Alpha Vantage.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging
from crewai.tools import tool

# Importa integração com Alpha Vantage e MCP
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.alpha_vantage_config import alpha_vantage_manager
from config.mcp_client import get_alpha_vantage_mcp_data, is_mcp_available, get_mcp_context

logger = logging.getLogger(__name__)


class YfinanceTools:
    """Ferramentas para obter dados financeiros do Yahoo Finance."""
    
    @staticmethod
    def obter_nome_empresa(symbol: str) -> str:
        """
        Obtém o nome completo da empresa pelo símbolo.
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA)
            
        Returns:
            Nome da empresa
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            name = info.get('longName') or info.get('shortName') or symbol
            sector = info.get('sector', 'Setor não disponível')
            industry = info.get('industry', 'Indústria não disponível')
            
            return f"""Empresa: {name}
Símbolo: {symbol}
Setor: {sector}
Indústria: {industry}"""
            
        except Exception as e:
            logger.error(f"Erro ao obter nome da empresa {symbol}: {e}")
            return f"Erro ao obter informações da empresa {symbol}: {str(e)}"

    @staticmethod
    def obter_informacoes_empresa(symbol: str) -> str:
        """
        Obtém informações gerais da empresa.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Informações formatadas da empresa
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Informações principais
            company_info = f"""INFORMAÇÕES DA EMPRESA - {symbol}

Nome: {info.get('longName', 'N/A')}
Setor: {info.get('sector', 'N/A')}
Indústria: {info.get('industry', 'N/A')}
País: {info.get('country', 'N/A')}
Website: {info.get('website', 'N/A')}

DADOS FUNDAMENTAIS:
Market Cap: {YfinanceTools._format_currency(info.get('marketCap'))}
Valor da Empresa: {YfinanceTools._format_currency(info.get('enterpriseValue'))}
P/L: {info.get('trailingPE', 'N/A')}
P/VPA: {info.get('priceToBook', 'N/A')}
Dividend Yield: {YfinanceTools._format_percentage(info.get('dividendYield'))}
ROE: {YfinanceTools._format_percentage(info.get('returnOnEquity'))}
ROA: {YfinanceTools._format_percentage(info.get('returnOnAssets'))}

PREÇO ATUAL:
Preço: R$ {info.get('currentPrice', 'N/A')}
Variação (52 semanas): R$ {info.get('fiftyTwoWeekLow', 'N/A')} - R$ {info.get('fiftyTwoWeekHigh', 'N/A')}
Volume médio: {YfinanceTools._format_number(info.get('averageVolume'))}

DESCRIÇÃO:
{info.get('longBusinessSummary', 'Descrição não disponível')[:500]}..."""

            return company_info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações da empresa {symbol}: {e}")
            return f"Erro ao obter informações da empresa {symbol}: {str(e)}"

    @staticmethod
    def obter_dividendos_empresa(symbol: str, period: str = "2y") -> str:
        """
        Obtém histórico de dividendos da empresa.
        
        Args:
            symbol: Símbolo da ação
            period: Período para análise (1y, 2y, 5y, max)
            
        Returns:
            Histórico de dividendos formatado
        """
        try:
            ticker = yf.Ticker(symbol)
            dividends = ticker.dividends
            
            if dividends.empty:
                return f"Nenhum dividendo encontrado para {symbol} no período {period}"
            
            # Filtra por período
            end_date = datetime.now()
            if period == "1y":
                start_date = end_date - timedelta(days=365)
            elif period == "2y":
                start_date = end_date - timedelta(days=730)
            elif period == "5y":
                start_date = end_date - timedelta(days=1825)
            else:
                start_date = dividends.index.min()
            
            recent_dividends = dividends[dividends.index >= start_date]
            
            result = f"HISTÓRICO DE DIVIDENDOS - {symbol} (Período: {period})\n\n"
            
            # Últimos dividendos
            result += "ÚLTIMOS DIVIDENDOS:\n"
            for date, value in recent_dividends.tail(10).items():
                result += f"{date.strftime('%d/%m/%Y')}: R$ {value:.4f}\n"
            
            # Estatísticas
            total_dividends = recent_dividends.sum()
            avg_dividend = recent_dividends.mean()
            dividend_count = len(recent_dividends)
            
            result += f"\nESTATÍSTICAS ({period}):\n"
            result += f"Total de dividendos: R$ {total_dividends:.4f}\n"
            result += f"Dividendo médio: R$ {avg_dividend:.4f}\n"
            result += f"Número de pagamentos: {dividend_count}\n"
            
            # Yield anualizado (aproximado)
            ticker_info = ticker.info
            current_price = ticker_info.get('currentPrice', 0)
            if current_price > 0:
                annual_yield = (total_dividends / len(period)) / current_price * 100
                result += f"Yield anualizado (aprox.): {annual_yield:.2f}%\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter dividendos de {symbol}: {e}")
            return f"Erro ao obter dividendos de {symbol}: {str(e)}"

    @staticmethod
    def obter_declaracoes_financeiras_empresa(symbol: str) -> str:
        """
        Obtém declarações financeiras da empresa.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Declarações financeiras formatadas
        """
        try:
            ticker = yf.Ticker(symbol)
            
            # DRE - Demonstração de Resultados
            income_stmt = ticker.financials
            
            if income_stmt.empty:
                return f"Demonstrações financeiras não disponíveis para {symbol}"
            
            result = f"DEMONSTRAÇÃO DE RESULTADOS - {symbol}\n\n"
            
            # Principais itens da DRE (últimos 4 anos)
            for column in income_stmt.columns[:4]:  # Últimos 4 anos
                year = column.strftime('%Y')
                result += f"ANO: {year}\n"
                
                revenue = income_stmt.loc['Total Revenue', column] if 'Total Revenue' in income_stmt.index else 0
                gross_profit = income_stmt.loc['Gross Profit', column] if 'Gross Profit' in income_stmt.index else 0
                operating_income = income_stmt.loc['Operating Income', column] if 'Operating Income' in income_stmt.index else 0
                net_income = income_stmt.loc['Net Income', column] if 'Net Income' in income_stmt.index else 0
                
                result += f"Receita Total: {YfinanceTools._format_currency(revenue)}\n"
                result += f"Lucro Bruto: {YfinanceTools._format_currency(gross_profit)}\n"
                result += f"Resultado Operacional: {YfinanceTools._format_currency(operating_income)}\n"
                result += f"Lucro Líquido: {YfinanceTools._format_currency(net_income)}\n"
                
                # Margens
                if revenue > 0:
                    gross_margin = (gross_profit / revenue) * 100
                    operating_margin = (operating_income / revenue) * 100
                    net_margin = (net_income / revenue) * 100
                    
                    result += f"Margem Bruta: {gross_margin:.1f}%\n"
                    result += f"Margem Operacional: {operating_margin:.1f}%\n"
                    result += f"Margem Líquida: {net_margin:.1f}%\n"
                
                result += "\n" + "-" * 40 + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter declarações financeiras de {symbol}: {e}")
            return f"Erro ao obter declarações financeiras de {symbol}: {str(e)}"

    @staticmethod
    def obter_balancos_financeiros_empresa(symbol: str) -> str:
        """
        Obtém balanços patrimoniais da empresa.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Balanços formatados
        """
        try:
            ticker = yf.Ticker(symbol)
            balance_sheet = ticker.balance_sheet
            
            if balance_sheet.empty:
                return f"Balanço patrimonial não disponível para {symbol}"
            
            result = f"BALANÇO PATRIMONIAL - {symbol}\n\n"
            
            # Últimos 4 anos
            for column in balance_sheet.columns[:4]:
                year = column.strftime('%Y')
                result += f"ANO: {year}\n"
                
                # Ativos
                total_assets = balance_sheet.loc['Total Assets', column] if 'Total Assets' in balance_sheet.index else 0
                current_assets = balance_sheet.loc['Current Assets', column] if 'Current Assets' in balance_sheet.index else 0
                cash = balance_sheet.loc['Cash And Cash Equivalents', column] if 'Cash And Cash Equivalents' in balance_sheet.index else 0
                
                # Passivos
                total_liab = balance_sheet.loc['Total Liab', column] if 'Total Liab' in balance_sheet.index else 0
                current_liab = balance_sheet.loc['Current Liabilities', column] if 'Current Liabilities' in balance_sheet.index else 0
                total_debt = balance_sheet.loc['Total Debt', column] if 'Total Debt' in balance_sheet.index else 0
                
                # Patrimônio
                stockholder_equity = balance_sheet.loc['Stockholders Equity', column] if 'Stockholders Equity' in balance_sheet.index else 0
                
                result += f"ATIVOS:\n"
                result += f"  Total de Ativos: {YfinanceTools._format_currency(total_assets)}\n"
                result += f"  Ativos Circulantes: {YfinanceTools._format_currency(current_assets)}\n"
                result += f"  Caixa e Equivalentes: {YfinanceTools._format_currency(cash)}\n"
                
                result += f"PASSIVOS:\n"
                result += f"  Total de Passivos: {YfinanceTools._format_currency(total_liab)}\n"
                result += f"  Passivos Circulantes: {YfinanceTools._format_currency(current_liab)}\n"
                result += f"  Dívida Total: {YfinanceTools._format_currency(total_debt)}\n"
                
                result += f"PATRIMÔNIO:\n"
                result += f"  Patrimônio Líquido: {YfinanceTools._format_currency(stockholder_equity)}\n"
                
                # Indicadores
                if current_liab > 0:
                    liquidity_ratio = current_assets / current_liab
                    result += f"  Liquidez Corrente: {liquidity_ratio:.2f}\n"
                
                if stockholder_equity > 0:
                    debt_to_equity = total_debt / stockholder_equity
                    result += f"  Dívida/Patrimônio: {debt_to_equity:.2f}\n"
                
                result += "\n" + "-" * 50 + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter balanço de {symbol}: {e}")
            return f"Erro ao obter balanço de {symbol}: {str(e)}"

    @staticmethod
    def obter_fluxo_caixa_empresa(symbol: str) -> str:
        """
        Obtém demonstração de fluxo de caixa da empresa.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Fluxo de caixa formatado
        """
        try:
            ticker = yf.Ticker(symbol)
            cashflow = ticker.cashflow
            
            if cashflow.empty:
                return f"Fluxo de caixa não disponível para {symbol}"
            
            result = f"DEMONSTRAÇÃO DE FLUXO DE CAIXA - {symbol}\n\n"
            
            # Últimos 4 anos
            for column in cashflow.columns[:4]:
                year = column.strftime('%Y')
                result += f"ANO: {year}\n"
                
                # Fluxo operacional
                operating_cf = cashflow.loc['Operating Cash Flow', column] if 'Operating Cash Flow' in cashflow.index else 0
                
                # Fluxo de investimento
                investing_cf = cashflow.loc['Investing Cash Flow', column] if 'Investing Cash Flow' in cashflow.index else 0
                capex = cashflow.loc['Capital Expenditures', column] if 'Capital Expenditures' in cashflow.index else 0
                
                # Fluxo de financiamento
                financing_cf = cashflow.loc['Financing Cash Flow', column] if 'Financing Cash Flow' in cashflow.index else 0
                
                # Variação de caixa
                change_in_cash = cashflow.loc['Change In Cash', column] if 'Change In Cash' in cashflow.index else 0
                
                result += f"FLUXO OPERACIONAL: {YfinanceTools._format_currency(operating_cf)}\n"
                result += f"FLUXO DE INVESTIMENTO: {YfinanceTools._format_currency(investing_cf)}\n"
                result += f"  CapEx: {YfinanceTools._format_currency(capex)}\n"
                result += f"FLUXO DE FINANCIAMENTO: {YfinanceTools._format_currency(financing_cf)}\n"
                result += f"VARIAÇÃO DE CAIXA: {YfinanceTools._format_currency(change_in_cash)}\n"
                
                # Fluxo de caixa livre
                if operating_cf != 0 and capex != 0:
                    free_cash_flow = operating_cf + capex  # CapEx já é negativo
                    result += f"FLUXO DE CAIXA LIVRE: {YfinanceTools._format_currency(free_cash_flow)}\n"
                
                result += "\n" + "-" * 50 + "\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter fluxo de caixa de {symbol}: {e}")
            return f"Erro ao obter fluxo de caixa de {symbol}: {str(e)}"

    @staticmethod
    def obter_ultimas_cotacoes(symbol: str, period: str = "1mo") -> str:
        """
        Obtém cotações recentes da ação.
        
        Args:
            symbol: Símbolo da ação
            period: Período (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            Cotações formatadas
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return f"Cotações não disponíveis para {symbol} no período {period}"
            
            result = f"COTAÇÕES RECENTES - {symbol} (Período: {period})\n\n"
            
            # Últimos 10 dias
            recent_data = hist.tail(10)
            
            result += "DATA\t\tABERTURA\tMÁXIMA\t\tMÍNIMA\t\tFECHAMENTO\tVOLUME\n"
            result += "-" * 80 + "\n"
            
            for date, row in recent_data.iterrows():
                result += f"{date.strftime('%d/%m/%Y')}\t"
                result += f"R$ {row['Open']:.2f}\t\t"
                result += f"R$ {row['High']:.2f}\t\t"
                result += f"R$ {row['Low']:.2f}\t\t"
                result += f"R$ {row['Close']:.2f}\t\t"
                result += f"{row['Volume']:,.0f}\n"
            
            # Estatísticas do período
            result += f"\nESTATÍSTICAS DO PERÍODO ({period}):\n"
            result += f"Preço máximo: R$ {hist['High'].max():.2f}\n"
            result += f"Preço mínimo: R$ {hist['Low'].min():.2f}\n"
            result += f"Preço médio: R$ {hist['Close'].mean():.2f}\n"
            result += f"Volume médio: {hist['Volume'].mean():,.0f}\n"
            
            # Variação no período
            first_close = hist['Close'].iloc[0]
            last_close = hist['Close'].iloc[-1]
            variation = ((last_close - first_close) / first_close) * 100
            
            result += f"Variação no período: {variation:.2f}%\n"
            
            # Volatilidade
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5) * 100  # Anualizada
            result += f"Volatilidade anualizada: {volatility:.2f}%\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao obter cotações de {symbol}: {e}")
            return f"Erro ao obter cotações de {symbol}: {str(e)}"

    @staticmethod
    def _format_currency(value: Optional[float]) -> str:
        """Formata valores monetários."""
        if value is None or pd.isna(value):
            return "N/A"
        
        if abs(value) >= 1e9:
            return f"R$ {value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"R$ {value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"R$ {value/1e3:.2f}K"
        else:
            return f"R$ {value:.2f}"

    @staticmethod
    def _format_percentage(value: Optional[float]) -> str:
        """Formata valores percentuais."""
        if value is None or pd.isna(value):
            return "N/A"
        return f"{value*100:.2f}%"

    @staticmethod
    def get_enhanced_financial_data_with_mcp(symbol: str) -> Dict[str, Any]:
        """
        Obtém dados financeiros usando MCP como fonte primária, 
        com fallback para Alpha Vantage tradicional e Yahoo Finance.
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA)
            
        Returns:
            Dicionário com dados financeiros aprimorados via MCP
        """
        logger.info(f"Coletando dados financeiros via MCP para {symbol}")
        
        # Dados básicos do Yahoo Finance
        basic_data = YfinanceTools.obter_info_completa(symbol)
        
        enhanced_data = {
            'symbol': symbol,
            'yahoo_finance': basic_data,
            'mcp_available': is_mcp_available(),
            'alpha_vantage_available': alpha_vantage_manager.is_available()
        }
        
        # Prioridade 1: MCP (Model Context Protocol)
        if is_mcp_available():
            try:
                # Converte símbolo brasileiro para formato Alpha Vantage
                av_symbol = symbol.replace('.SA', '')
                
                # Obtém dados via MCP
                mcp_data = get_alpha_vantage_mcp_data(av_symbol)
                
                if mcp_data.get('mcp_available'):
                    enhanced_data['mcp_data'] = mcp_data
                    enhanced_data['primary_source'] = 'mcp'
                    
                    # Gera contexto estruturado para LLM
                    mcp_context = get_mcp_context(av_symbol, mcp_data)
                    if mcp_context:
                        enhanced_data['mcp_context'] = mcp_context
                    
                    logger.info(f"Dados MCP coletados com sucesso para {symbol}")
                    return enhanced_data
                else:
                    logger.warning(f"MCP configurado mas sem dados para {symbol}")
                    
            except Exception as e:
                logger.error(f"Erro ao coletar dados MCP para {symbol}: {e}")
                enhanced_data['mcp_error'] = str(e)
        
        # Prioridade 2: Alpha Vantage tradicional (fallback)
        if alpha_vantage_manager.is_available():
            try:
                av_symbol = symbol.replace('.SA', '')
                av_data = alpha_vantage_manager.get_enhanced_financial_data(av_symbol)
                
                if av_data.get('alpha_vantage_available'):
                    enhanced_data['alpha_vantage'] = av_data
                    enhanced_data['primary_source'] = 'alpha_vantage'
                    
                    # Contexto tradicional
                    context = alpha_vantage_manager.get_mcp_context(av_symbol)
                    if context:
                        enhanced_data['alpha_vantage_context'] = context
                    
                    logger.info(f"Dados Alpha Vantage (fallback) coletados para {symbol}")
                else:
                    logger.warning(f"Alpha Vantage disponível mas sem dados para {symbol}")
                    
            except Exception as e:
                logger.error(f"Erro ao coletar dados Alpha Vantage para {symbol}: {e}")
                enhanced_data['alpha_vantage_error'] = str(e)
        
        # Define fonte primária como Yahoo Finance se nenhuma outra funcionou
        if 'primary_source' not in enhanced_data:
            enhanced_data['primary_source'] = 'yahoo_finance'
        
        return enhanced_data

    @staticmethod
    def compare_data_sources(symbol: str) -> Dict[str, Any]:
        """
        Compara dados entre Yahoo Finance e Alpha Vantage para validação.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Comparação entre as fontes de dados
        """
        if not alpha_vantage_manager.is_available():
            return {'comparison_available': False, 'reason': 'Alpha Vantage not configured'}
        
        logger.info(f"Comparando dados de fontes para {symbol}")
        
        # Dados Yahoo Finance
        yf_data = YfinanceTools.obter_info_completa(symbol)
        
        # Dados Alpha Vantage
        av_symbol = symbol.replace('.SA', '')
        av_overview = alpha_vantage_manager.get_company_overview(av_symbol)
        
        if not av_overview:
            return {'comparison_available': False, 'reason': 'No Alpha Vantage data available'}
        
        comparison = {
            'comparison_available': True,
            'symbol': symbol,
            'timestamp': datetime.now().isoformat(),
            'metrics_comparison': {}
        }
        
        # Compara métricas chave
        metrics_map = {
            'market_cap': ('marketCap', 'market_cap'),
            'pe_ratio': ('trailingPE', 'pe_ratio'),
            'beta': ('beta', 'beta'),
            'eps': ('trailingEps', 'eps'),
            'book_value': ('bookValue', 'book_value')
        }
        
        for metric, (yf_key, av_key) in metrics_map.items():
            yf_value = yf_data.get(yf_key)
            av_value = av_overview.get(av_key)
            
            if yf_value is not None and av_value is not None:
                try:
                    yf_num = float(yf_value)
                    av_num = float(av_value)
                    
                    # Calcula diferença percentual
                    diff_pct = abs(yf_num - av_num) / yf_num * 100 if yf_num != 0 else 0
                    
                    comparison['metrics_comparison'][metric] = {
                        'yahoo_finance': yf_num,
                        'alpha_vantage': av_num,
                        'difference_percent': diff_pct,
                        'match_status': 'close' if diff_pct < 5 else 'different'
                    }
                except (ValueError, TypeError):
                    comparison['metrics_comparison'][metric] = {
                        'yahoo_finance': yf_value,
                        'alpha_vantage': av_value,
                        'match_status': 'format_error'
                    }
        
        return comparison

    @staticmethod
    def get_financial_summary_with_all_sources(symbol: str) -> str:
        """
        Gera resumo financeiro combinando Yahoo Finance, MCP e Alpha Vantage.
        
        Args:
            symbol: Símbolo da ação
            
        Returns:
            Resumo textual com dados de todas as fontes disponíveis
        """
        enhanced_data = YfinanceTools.get_enhanced_financial_data_with_mcp(symbol)
        
        summary_parts = [
            f"=== ANÁLISE FINANCEIRA COMPLETA - {symbol} ===",
            f"Data da análise: {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            f"Fonte primária: {enhanced_data.get('primary_source', 'yahoo_finance').upper()}",
            ""
        ]
        
        # Dados Yahoo Finance (base)
        yf_data = enhanced_data.get('yahoo_finance', {})
        if yf_data:
            summary_parts.extend([
                "📊 DADOS YAHOO FINANCE (BASE):",
                f"• Empresa: {yf_data.get('longName', 'N/A')}",
                f"• Setor: {yf_data.get('sector', 'N/A')}",
                f"• Preço atual: R$ {yf_data.get('currentPrice', 'N/A')}",
                f"• Market Cap: {YfinanceTools._format_number(yf_data.get('marketCap'))}",
                f"• P/L: {yf_data.get('trailingPE', 'N/A')}",
                f"• ROE: {YfinanceTools._format_percentage(yf_data.get('returnOnEquity'))}",
                ""
            ])
        
        # Dados MCP (prioridade)
        if enhanced_data.get('mcp_available') and 'mcp_data' in enhanced_data:
            mcp_data = enhanced_data['mcp_data']
            
            summary_parts.extend([
                "🤖 DADOS MCP (ALPHA VANTAGE - PRIORIDADE):",
                "Source: Model Context Protocol - https://mcp.alphavantage.co/",
                ""
            ])
            
            # Company overview via MCP
            if 'company_overview' in mcp_data:
                overview = mcp_data['company_overview']
                summary_parts.extend([
                    "FUNDAMENTALS (MCP):",
                    f"• Empresa: {overview.get('name', 'N/A')}",
                    f"• Setor: {overview.get('sector', 'N/A')}",
                    f"• Indústria: {overview.get('industry', 'N/A')}",
                    f"• P/L: {overview.get('pe_ratio', 'N/A')}",
                    f"• PEG Ratio: {overview.get('peg_ratio', 'N/A')}",
                    f"• ROE: {overview.get('roe', 'N/A')}",
                    f"• Margem de Lucro: {overview.get('profit_margin', 'N/A')}",
                    f"• EBITDA: {overview.get('ebitda', 'N/A')}",
                    ""
                ])
            
            # Financial statements via MCP
            if 'financial_statements' in mcp_data:
                summary_parts.extend([
                    "DEMONSTRAÇÕES FINANCEIRAS (MCP):",
                    "• Demonstração de Resultado: Disponível",
                    "• Balanço Patrimonial: Disponível",
                    "• Fluxo de Caixa: Disponível",
                    "• Histórico de Earnings: Disponível",
                    ""
                ])
            
            # Contexto MCP se disponível
            if 'mcp_context' in enhanced_data:
                summary_parts.extend([
                    "🔗 CONTEXTO MCP ESTRUTURADO:",
                    "Dados otimizados para análise via LLM",
                    "Formato padronizado e estruturado",
                    "Acesso em tempo real via protocolo MCP",
                    ""
                ])
        
        # Dados Alpha Vantage tradicional (fallback)
        elif enhanced_data.get('alpha_vantage_available') and 'alpha_vantage' in enhanced_data:
            av_data = enhanced_data['alpha_vantage']
            overview = av_data.get('company_overview', {})
            
            if overview:
                summary_parts.extend([
                    "🔍 DADOS ALPHA VANTAGE (FALLBACK):",
                    f"• Empresa: {overview.get('name', 'N/A')}",
                    f"• Setor: {overview.get('sector', 'N/A')}",
                    f"• Indústria: {overview.get('industry', 'N/A')}",
                    f"• P/L: {overview.get('pe_ratio', 'N/A')}",
                    f"• PEG Ratio: {overview.get('peg_ratio', 'N/A')}",
                    f"• ROE: {overview.get('roe', 'N/A')}",
                    f"• Margem de Lucro: {overview.get('profit_margin', 'N/A')}",
                    ""
                ])
        else:
            summary_parts.extend([
                "⚠️ DADOS AVANÇADOS:",
                "MCP: Não configurado ou indisponível",
                "Alpha Vantage: Não configurado ou indisponível",
                "Configure ALPHA_VANTAGE_API_KEY para dados completos",
                "MCP oferece a melhor experiência para análise de dados",
                ""
            ])
        
        # Status das fontes de dados
        summary_parts.extend([
            "📋 STATUS DAS FONTES:",
            f"• Yahoo Finance: ✅ Ativo (base)",
            f"• MCP Alpha Vantage: {'✅ Ativo' if enhanced_data.get('mcp_available') else '❌ Inativo'}",
            f"• Alpha Vantage: {'✅ Ativo' if enhanced_data.get('alpha_vantage_available') else '❌ Inativo'}",
            ""
        ])
        
        # Recomendações
        if not enhanced_data.get('mcp_available'):
            summary_parts.extend([
                "� RECOMENDAÇÕES:",
                "• Configure Alpha Vantage API para MCP",
                "• MCP oferece dados estruturados em tempo real",
                "• Melhor precisão e formato otimizado para IA",
                "• Documentação: https://mcp.alphavantage.co/",
                ""
            ])
        
        return "\n".join(summary_parts)

    @staticmethod
    def _format_number(value: Optional[float]) -> str:
        """Formata números grandes."""
        if value is None or pd.isna(value):
            return "N/A"
        
        if abs(value) >= 1e9:
            return f"{value/1e9:.2f}B"
        elif abs(value) >= 1e6:
            return f"{value/1e6:.2f}M"
        elif abs(value) >= 1e3:
            return f"{value/1e3:.2f}K"
        else:
            return f"{value:,.0f}"


# Ferramentas decoradas para CrewAI
@tool
def obter_nome_empresa(symbol: str) -> str:
    """
    Obtém o nome da empresa a partir do símbolo da ação.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Nome da empresa
    """
    return YfinanceTools.obter_nome_empresa(symbol)


@tool
def obter_informacoes_empresa(symbol: str) -> str:
    """
    Obtém informações detalhadas da empresa usando dados integrados.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Informações detalhadas da empresa
    """
    return YfinanceTools.obter_informacoes_empresa(symbol)


@tool
def obter_dividendos_empresa(symbol: str) -> str:
    """
    Obtém histórico de dividendos da empresa.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Histórico de dividendos formatado
    """
    return YfinanceTools.obter_dividendos_empresa(symbol)


@tool
def obter_declaracoes_financeiras_empresa(symbol: str) -> str:
    """
    Obtém demonstrações de resultados (DRE) da empresa.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Demonstrações financeiras formatadas
    """
    return YfinanceTools.obter_declaracoes_financeiras_empresa(symbol)


@tool
def obter_balancos_financeiros_empresa(symbol: str) -> str:
    """
    Obtém balanços patrimoniais da empresa.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Balanços patrimoniais formatados
    """
    return YfinanceTools.obter_balancos_financeiros_empresa(symbol)


@tool
def obter_fluxo_caixa_empresa(symbol: str) -> str:
    """
    Obtém demonstrações de fluxo de caixa da empresa.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        
    Returns:
        Fluxo de caixa formatado
    """
    return YfinanceTools.obter_fluxo_caixa_empresa(symbol)


@tool
def obter_ultimas_cotacoes(symbol: str, period: str = "1mo") -> str:
    """
    Obtém as últimas cotações da ação.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        period: Período das cotações (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
        
    Returns:
        Cotações formatadas
    """
    return YfinanceTools.obter_ultimas_cotacoes(symbol, period)
