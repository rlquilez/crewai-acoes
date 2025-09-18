"""
Ferramentas para busca na internet e notícias usando SearXNG e Browserless.
"""

import requests
import httpx
import asyncio
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime, timedelta
import json
import os
from urllib.parse import quote, urljoin
from crewai.tools import tool

logger = logging.getLogger(__name__)


class SearchTools:
    """Ferramentas para busca na internet e notícias usando SearXNG."""
    
    @staticmethod
    def search_internet(query: str, num_results: int = 5) -> str:
        """
        Busca na internet usando SearXNG ou fallback para Google Custom Search API.
        
        Args:
            query: Termo de busca
            num_results: Número de resultados desejados
            
        Returns:
            Resultados da busca formatados
        """
        try:
            # Tenta usar SearXNG primeiro
            searxng_url = os.getenv('SEARXNG_URL')
            if searxng_url:
                return SearchTools._search_with_searxng(query, num_results)
            
            # Fallback para Google Custom Search API
            api_key = os.getenv('GOOGLE_API_KEY')
            search_engine_id = os.getenv('GOOGLE_CSE_ID')
            
            if api_key and search_engine_id:
                return SearchTools._search_with_google(query, num_results, api_key, search_engine_id)
            
            # Se nenhuma API estiver configurada, simula busca
            return SearchTools._simulate_search(query, num_results)
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return SearchTools._simulate_search(query, num_results)

    @staticmethod
    def _search_with_searxng(query: str, num_results: int) -> str:
        """
        Realiza busca usando SearXNG.
        
        Args:
            query: Termo de busca
            num_results: Número de resultados
            
        Returns:
            Resultados formatados
        """
        try:
            searxng_url = os.getenv('SEARXNG_URL')
            api_key = os.getenv('SEARXNG_API_KEY')
            timeout = int(os.getenv('SEARXNG_TIMEOUT', '30'))
            safe_search = os.getenv('SEARXNG_SAFE_SEARCH', '0')
            language = os.getenv('SEARXNG_LANGUAGE', 'pt-BR')
            categories = os.getenv('SEARXNG_CATEGORIES', 'general')
            
            search_url = urljoin(searxng_url, '/search')
            
            params = {
                'q': query,
                'format': 'json',
                'safesearch': safe_search,
                'language': language,
                'categories': categories
            }
            
            headers = {}
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'
            
            response = requests.get(
                search_url, 
                params=params, 
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])[:num_results]
            
            formatted_results = f"Resultados da busca SearXNG para '{query}':\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result.get('title', 'Sem título')}\n"
                formatted_results += f"   Link: {result.get('url', '')}\n"
                formatted_results += f"   Resumo: {result.get('content', 'Sem descrição')}\n"
                formatted_results += f"   Engine: {result.get('engine', 'N/A')}\n\n"
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca SearXNG: {e}")
            raise

    @staticmethod
    def _search_with_google(query: str, num_results: int, api_key: str, search_engine_id: str) -> str:
        """
        Realiza busca usando Google Custom Search API (fallback).
        
        Args:
            query: Termo de busca
            num_results: Número de resultados
            api_key: Chave da API Google
            search_engine_id: ID do motor de busca
            
        Returns:
            Resultados formatados
        """
        try:
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': api_key,
                'cx': search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
            
            formatted_results = f"Resultados da busca Google para '{query}':\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   Link: {result['link']}\n"
                formatted_results += f"   Resumo: {result['snippet']}\n\n"
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca Google: {e}")
            raise
            results = []
            
            if 'items' in data:
                for item in data['items']:
                    results.append({
                        'title': item.get('title', ''),
                        'link': item.get('link', ''),
                        'snippet': item.get('snippet', '')
                    })
            
            formatted_results = f"Resultados da busca para '{query}':\n\n"
            for i, result in enumerate(results, 1):
                formatted_results += f"{i}. {result['title']}\n"
                formatted_results += f"   Link: {result['link']}\n"
                formatted_results += f"   Resumo: {result['snippet']}\n\n"
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Erro na busca: {e}")
            return SearchTools._simulate_search(query, num_results)

    @staticmethod
    def search_news(query: str, days_back: int = 7, language: str = 'pt') -> str:
        """
        Busca notícias recentes relacionadas ao termo.
        
        Args:
            query: Termo de busca
            days_back: Número de dias para buscar notícias
            language: Idioma das notícias
            
        Returns:
            Notícias encontradas formatadas
        """
        try:
            # Simula busca de notícias (em produção, usar News API)
            api_key = os.getenv('NEWS_API_KEY')
            
            if not api_key:
                return SearchTools._simulate_news_search(query, days_back)
            
            from_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            
            url = "https://newsapi.org/v2/everything"
            params = {
                'apiKey': api_key,
                'q': query,
                'from': from_date,
                'language': language,
                'sortBy': 'publishedAt',
                'pageSize': 10
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get('articles', [])
            
            formatted_news = f"Notícias recentes sobre '{query}' (últimos {days_back} dias):\n\n"
            
            for i, article in enumerate(articles[:5], 1):
                formatted_news += f"{i}. {article.get('title', 'Sem título')}\n"
                formatted_news += f"   Fonte: {article.get('source', {}).get('name', 'Fonte desconhecida')}\n"
                formatted_news += f"   Data: {article.get('publishedAt', 'Data não disponível')}\n"
                formatted_news += f"   Descrição: {article.get('description', 'Sem descrição')}\n"
                formatted_news += f"   Link: {article.get('url', '')}\n\n"
            
            return formatted_news
            
        except Exception as e:
            logger.error(f"Erro na busca de notícias: {e}")
            return SearchTools._simulate_news_search(query, days_back)

    @staticmethod
    def search_financial_news(symbol: str, days_back: int = 7) -> str:
        """
        Busca notícias financeiras específicas de uma empresa/ação.
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA)
            days_back: Número de dias para buscar
            
        Returns:
            Notícias financeiras formatadas
        """
        try:
            # Remove .SA do símbolo para busca mais ampla
            company_symbol = symbol.replace('.SA', '')
            
            queries = [
                f"{company_symbol} ação bolsa valores",
                f"{company_symbol} resultados financeiros",
                f"{company_symbol} B3 São Paulo"
            ]
            
            all_news = ""
            for query in queries:
                news = SearchTools.search_news(query, days_back)
                all_news += news + "\n" + "="*50 + "\n"
            
            return f"Notícias financeiras para {symbol}:\n\n{all_news}"
            
        except Exception as e:
            logger.error(f"Erro na busca de notícias financeiras: {e}")
            return f"Erro ao buscar notícias financeiras para {symbol}: {str(e)}"

    @staticmethod
    def _simulate_search(query: str, num_results: int) -> str:
        """Simula resultados de busca quando API não está disponível."""
        return f"""Busca simulada para '{query}' (API não configurada):

1. Resultados relevantes sobre {query}
   Link: https://example.com/resultado1
   Resumo: Informações gerais sobre {query} e análises de mercado.

2. Análise de mercado - {query}
   Link: https://example.com/resultado2
   Resumo: Análise técnica e fundamentalista sobre {query}.

3. Notícias recentes - {query}
   Link: https://example.com/resultado3
   Resumo: Últimas notícias e movimentações relacionadas a {query}.

Nota: Configure as APIs do Google e News API para resultados reais.
"""

    @staticmethod
    def _simulate_news_search(query: str, days_back: int) -> str:
        """Simula busca de notícias quando API não está disponível."""
        return f"""Notícias simuladas sobre '{query}' (últimos {days_back} dias):

1. Movimento de alta para {query}
   Fonte: Portal de Notícias
   Data: {datetime.now().strftime('%Y-%m-%d')}
   Descrição: Análise indica tendência positiva para {query} baseada em indicadores técnicos.

2. Resultados trimestrais de {query}
   Fonte: Valor Econômico
   Data: {(datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')}
   Descrição: Empresa divulga resultados do último trimestre com crescimento nas receitas.

3. Recomendação de analistas para {query}
   Fonte: InfoMoney
   Data: {(datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')}
   Descrição: Analistas recomendam compra baseada em fundamentals sólidos.

Nota: Configure a News API para notícias reais.
"""


# Ferramentas decoradas para CrewAI
@tool
def search_internet(query: str, num_results: int = 5) -> str:
    """
    Busca na internet usando SearXNG ou fallback para Google Custom Search API.
    
    Args:
        query: Termo de busca
        num_results: Número de resultados desejados (default: 5)
        
    Returns:
        Resultados da busca formatados
    """
    return SearchTools.search_internet(query, num_results)


@tool
def search_news(query: str, num_results: int = 5) -> str:
    """
    Busca notícias na internet usando SearXNG ou Google News.
    
    Args:
        query: Termo de busca para notícias
        num_results: Número de resultados desejados (default: 5)
        
    Returns:
        Notícias encontradas formatadas
    """
    return SearchTools.search_news(query, num_results)


@tool
def search_financial_news(query: str, num_results: int = 5) -> str:
    """
    Busca notícias financeiras específicas usando NewsAPI ou SearXNG.
    
    Args:
        query: Termo de busca para notícias financeiras
        num_results: Número de resultados desejados (default: 5)
        
    Returns:
        Notícias financeiras encontradas formatadas
    """
    return SearchTools.search_financial_news(query, num_results)
