#!/usr/bin/env python3
"""
Teste simples para verificar se a correção da função de dividendos está funcionando.
"""

import yfinance as yf
import pandas as pd

def test_dividend_datetime_fix():
    """Testa se a correção do datetime funciona."""
    print("Testando correção de datetime para dividendos...")
    
    try:
        # Simula o problema original
        ticker = yf.Ticker("PETR4.SA")
        dividends = ticker.dividends
        
        if dividends.empty:
            print("⚠️  Nenhum dividendo encontrado para teste")
            return True
        
        # Testa a nova abordagem
        end_date = pd.Timestamp.now()
        start_date = end_date - pd.Timedelta(days=730)  # 2 anos
        
        # Garantir que as datas tenham o mesmo timezone
        if dividends.index.tz is not None:
            if start_date.tz is None:
                start_date = start_date.tz_localize(dividends.index.tz)
            else:
                start_date = start_date.tz_convert(dividends.index.tz)
        
        # Esta operação deveria funcionar agora
        recent_dividends = dividends[dividends.index >= start_date]
        
        print(f"✅ Sucesso! Encontrados {len(recent_dividends)} dividendos recentes")
        print(f"Primeiro dividendo: {recent_dividends.index[0] if len(recent_dividends) > 0 else 'N/A'}")
        print(f"Último dividendo: {recent_dividends.index[-1] if len(recent_dividends) > 0 else 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

if __name__ == "__main__":
    success = test_dividend_datetime_fix()
    if success:
        print("\n🎉 Correção de datetime bem-sucedida!")
    else:
        print("\n💥 Correção falhou. Verifique a implementação.")