#!/usr/bin/env python3
"""
Script para testar a correção da limitação de dados históricos no yfinance_tools.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.tools.yfinance_tools import YfinanceTools
    from src.tools.calculator_tools import CalculatorTools
except ImportError:
    # Fallback para executar dentro do src/
    from tools.yfinance_tools import YfinanceTools
    from tools.calculator_tools import CalculatorTools

def test_fix():
    """Testa se a correção resolve o problema de limitação de dados."""
    
    symbol = "PETR4.SA"
    print(f"🔍 Testando correção para {symbol}...")
    
    # 1. Teste da nova função obter_precos_historicos
    print("\n1. Testando obter_precos_historicos...")
    prices = YfinanceTools.obter_precos_historicos(symbol, period="3mo", max_points=50)
    
    print(f"   Preços obtidos: {len(prices)}")
    if prices:
        print(f"   Primeiros 5 preços: {prices[:5]}")
        print(f"   Últimos 5 preços: {prices[-5:]}")
    else:
        print("   ❌ Nenhum preço obtido")
        return False
    
    # 2. Teste de cálculo de média móvel com diferentes períodos
    print("\n2. Testando cálculos de médias móveis...")
    
    test_windows = [10, 20, 50]
    for window in test_windows:
        print(f"\n   Testando MA{window}:")
        if len(prices) >= window:
            result = CalculatorTools.calculate_moving_average(prices, window)
            print(f"   ✅ MA{window}: {result}")
        else:
            print(f"   ⚠️  Dados insuficientes para MA{window} (precisa: {window}, tem: {len(prices)})")
    
    # 3. Teste da função modificada obter_ultimas_cotacoes
    print("\n3. Testando obter_ultimas_cotacoes modificada...")
    cotacoes = YfinanceTools.obter_ultimas_cotacoes(symbol, period="1mo", limit_display=5)
    print(f"   ✅ Cotações (5 últimas):")
    print(f"   {cotacoes[:200]}...")  # Mostra início apenas
    
    # 4. Teste com dados para MA200 (mais desafiador)
    print("\n4. Testando MA200 (caso mais complexo)...")
    prices_long = YfinanceTools.obter_precos_historicos(symbol, period="1y", max_points=250)
    print(f"   Preços longos obtidos: {len(prices_long)}")
    
    if len(prices_long) >= 200:
        result_ma200 = CalculatorTools.calculate_moving_average(prices_long, 200)
        print(f"   ✅ MA200: {result_ma200}")
    else:
        print(f"   ⚠️  Dados insuficientes para MA200 (precisa: 200, tem: {len(prices_long)})")
    
    print("\n🎉 Teste concluído com sucesso!")
    return True

if __name__ == "__main__":
    test_fix()