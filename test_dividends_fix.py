#!/usr/bin/env python3
"""
Teste para verificar se a correção da função de dividendos está funcionando.
"""

import sys
import os
sys.path.append('/Users/rodrigo/Documents/PESSOAL/dev/crewai-acoes/src')

from tools.yfinance_tools import YfinanceTools

def test_dividends():
    """Testa a função de obtenção de dividendos."""
    print("Testando obtenção de dividendos para PETR4.SA...")
    
    try:
        result = YfinanceTools.obter_dividendos_empresa("PETR4.SA", "2y")
        print("✅ Sucesso!")
        print(result[:200] + "..." if len(result) > 200 else result)
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_dividends()
    if success:
        print("\n🎉 Teste passou! A correção foi bem-sucedida.")
    else:
        print("\n💥 Teste falhou. Verifique a implementação.")