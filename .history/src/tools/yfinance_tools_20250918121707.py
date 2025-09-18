"""
Ferramentas para obter dados financeiros usando Yahoo Finance.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import logging

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
