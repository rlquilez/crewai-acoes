# Script para testar os serviços SearXNG e Browserless
import os
import sys
import requests
import json
from urllib.parse import urljoin

def test_searxng():
    """Testa a conexão com SearXNG"""
    searxng_url = os.getenv('SEARXNG_URL', 'http://localhost:8080')
    
    print(f"🔍 Testando SearXNG em: {searxng_url}")
    
    try:
        # Teste de conectividade
        response = requests.get(searxng_url, timeout=10)
        if response.status_code == 200:
            print("✅ SearXNG está respondendo")
        else:
            print(f"❌ SearXNG retornou status: {response.status_code}")
            return False
            
        # Teste de busca
        search_url = urljoin(searxng_url, '/search')
        params = {
            'q': 'Petrobras PETR4',
            'format': 'json',
            'categories': 'general'
        }
        
        response = requests.get(search_url, params=params, timeout=10)
        if response.status_code == 200:
            data = response.json()
            results_count = len(data.get('results', []))
            print(f"✅ Busca funcionando - {results_count} resultados encontrados")
            return True
        else:
            print(f"❌ Erro na busca: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com SearXNG: {e}")
        return False

def test_browserless():
    """Testa a conexão com Browserless"""
    browserless_url = os.getenv('BROWSERLESS_URL', 'http://localhost:3000')
    
    print(f"🌐 Testando Browserless em: {browserless_url}")
    
    try:
        # Teste de conectividade - endpoint de status
        health_url = urljoin(browserless_url, '/pressure')
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Browserless está respondendo - Pressão: {data.get('pressure', 'N/A')}")
        else:
            print(f"❌ Browserless retornou status: {response.status_code}")
            return False
            
        # Teste de scraping simples
        scrape_url = urljoin(browserless_url, '/content')
        payload = {
            'url': 'https://httpbin.org/get'
        }
        
        response = requests.post(scrape_url, json=payload, timeout=30)
        if response.status_code == 200:
            print("✅ Scraping funcionando")
            return True
        else:
            print(f"❌ Erro no scraping: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro de conexão com Browserless: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🧪 Iniciando testes dos serviços...\n")
    
    # Verifica se as variáveis de ambiente estão configuradas
    searxng_url = os.getenv('SEARXNG_URL')
    browserless_url = os.getenv('BROWSERLESS_URL')
    
    if not searxng_url:
        print("⚠️ SEARXNG_URL não configurado, usando padrão: http://localhost:8080")
    
    if not browserless_url:
        print("⚠️ BROWSERLESS_URL não configurado, usando padrão: http://localhost:3000")
    
    print()
    
    # Executa testes
    searxng_ok = test_searxng()
    print()
    browserless_ok = test_browserless()
    
    print("\n" + "="*50)
    print("📊 RESUMO DOS TESTES")
    print("="*50)
    print(f"SearXNG: {'✅ OK' if searxng_ok else '❌ FALHOU'}")
    print(f"Browserless: {'✅ OK' if browserless_ok else '❌ FALHOU'}")
    
    if searxng_ok and browserless_ok:
        print("\n🎉 Todos os serviços estão funcionando!")
        return 0
    else:
        print("\n⚠️ Alguns serviços apresentaram problemas.")
        print("\n💡 Dicas para resolver:")
        if not searxng_ok:
            print("- Verifique se o SearXNG está rodando: docker-compose up searxng")
        if not browserless_ok:
            print("- Verifique se o Browserless está rodando: docker-compose up browserless")
        print("- Aguarde alguns segundos para os serviços iniciarem completamente")
        print("- Verifique os logs: docker-compose logs searxng browserless")
        return 1

if __name__ == "__main__":
    sys.exit(main())
