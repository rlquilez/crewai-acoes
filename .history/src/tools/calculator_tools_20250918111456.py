"""
Ferramentas para cálculos financeiros e matemáticos.
"""

import math
import numpy as np
from typing import Union, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CalculatorTools:
    """Ferramentas para cálculos financeiros e matemáticos."""
    
    @staticmethod
    def calculate(expression: str) -> str:
        """
        Avalia expressões matemáticas simples de forma segura.
        
        Args:
            expression: Expressão matemática como string
            
        Returns:
            Resultado do cálculo como string
        """
        try:
            # Remove espaços e caracteres inválidos
            expression = expression.strip()
            
            # Lista de operações permitidas
            allowed_chars = set("0123456789+-*/().% ")
            if not all(c in allowed_chars for c in expression):
                return "Erro: Expressão contém caracteres não permitidos"
            
            # Avalia a expressão de forma segura
            result = eval(expression, {"__builtins__": {}}, {})
            
            return f"Resultado de '{expression}': {result}"
            
        except ZeroDivisionError:
            return "Erro: Divisão por zero"
        except Exception as e:
            logger.error(f"Erro no cálculo '{expression}': {e}")
            return f"Erro no cálculo: {str(e)}"

    @staticmethod
    def calculate_percentage_change(old_value: float, new_value: float) -> str:
        """
        Calcula a variação percentual entre dois valores.
        
        Args:
            old_value: Valor antigo
            new_value: Valor novo
            
        Returns:
            Variação percentual formatada
        """
        try:
            if old_value == 0:
                return "Erro: Valor inicial não pode ser zero"
            
            change = ((new_value - old_value) / old_value) * 100
            
            return f"Variação: {change:.2f}% (de {old_value} para {new_value})"
            
        except Exception as e:
            logger.error(f"Erro no cálculo de variação: {e}")
            return f"Erro no cálculo de variação: {str(e)}"

    @staticmethod
    def calculate_compound_return(initial_value: float, final_value: float, periods: int) -> str:
        """
        Calcula o retorno composto anualizado.
        
        Args:
            initial_value: Valor inicial
            final_value: Valor final
            periods: Número de períodos (anos)
            
        Returns:
            Retorno composto anualizado
        """
        try:
            if initial_value <= 0 or periods <= 0:
                return "Erro: Valores devem ser positivos"
            
            cagr = ((final_value / initial_value) ** (1 / periods)) - 1
            
            return f"CAGR: {cagr:.2%} ao ano (de {initial_value} para {final_value} em {periods} anos)"
            
        except Exception as e:
            logger.error(f"Erro no cálculo CAGR: {e}")
            return f"Erro no cálculo CAGR: {str(e)}"

    @staticmethod
    def calculate_volatility(prices: List[float]) -> str:
        """
        Calcula a volatilidade de uma série de preços.
        
        Args:
            prices: Lista de preços
            
        Returns:
            Volatilidade formatada
        """
        try:
            if len(prices) < 2:
                return "Erro: Necessário pelo menos 2 preços"
            
            returns = []
            for i in range(1, len(prices)):
                ret = (prices[i] - prices[i-1]) / prices[i-1]
                returns.append(ret)
            
            volatility = np.std(returns) * math.sqrt(252)  # Anualizada
            
            return f"Volatilidade anualizada: {volatility:.2%}"
            
        except Exception as e:
            logger.error(f"Erro no cálculo de volatilidade: {e}")
            return f"Erro no cálculo de volatilidade: {str(e)}"

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> str:
        """
        Calcula o Relative Strength Index (RSI).
        
        Args:
            prices: Lista de preços
            period: Período para cálculo (padrão: 14)
            
        Returns:
            RSI formatado
        """
        try:
            if len(prices) < period + 1:
                return f"Erro: Necessário pelo menos {period + 1} preços"
            
            gains = []
            losses = []
            
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                rsi = 100
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))
            
            interpretation = ""
            if rsi > 70:
                interpretation = " (Sobrecomprado)"
            elif rsi < 30:
                interpretation = " (Sobrevendido)"
            else:
                interpretation = " (Neutro)"
            
            return f"RSI ({period} períodos): {rsi:.2f}{interpretation}"
            
        except Exception as e:
            logger.error(f"Erro no cálculo RSI: {e}")
            return f"Erro no cálculo RSI: {str(e)}"

    @staticmethod
    def calculate_moving_average(prices: List[float], period: int) -> str:
        """
        Calcula a média móvel simples.
        
        Args:
            prices: Lista de preços
            period: Período para média móvel
            
        Returns:
            Média móvel formatada
        """
        try:
            if len(prices) < period:
                return f"Erro: Necessário pelo menos {period} preços"
            
            recent_prices = prices[-period:]
            ma = sum(recent_prices) / len(recent_prices)
            
            current_price = prices[-1]
            trend = "Alta" if current_price > ma else "Baixa"
            
            return f"MA{period}: {ma:.2f} (Preço atual: {current_price:.2f}, Tendência: {trend})"
            
        except Exception as e:
            logger.error(f"Erro no cálculo MA: {e}")
            return f"Erro no cálculo MA: {str(e)}"

    @staticmethod
    def calculate_support_resistance(prices: List[float], window: int = 20) -> str:
        """
        Identifica níveis de suporte e resistência.
        
        Args:
            prices: Lista de preços
            window: Janela para análise
            
        Returns:
            Níveis de suporte e resistência
        """
        try:
            if len(prices) < window:
                return f"Erro: Necessário pelo menos {window} preços"
            
            recent_prices = prices[-window:]
            support = min(recent_prices)
            resistance = max(recent_prices)
            current_price = prices[-1]
            
            # Calcula distância aos níveis
            support_distance = ((current_price - support) / support) * 100
            resistance_distance = ((resistance - current_price) / current_price) * 100
            
            return f"""Níveis técnicos (últimos {window} períodos):
Suporte: {support:.2f} (Distância: {support_distance:.1f}%)
Resistência: {resistance:.2f} (Distância: {resistance_distance:.1f}%)
Preço atual: {current_price:.2f}"""
            
        except Exception as e:
            logger.error(f"Erro no cálculo de suporte/resistência: {e}")
            return f"Erro no cálculo: {str(e)}"
