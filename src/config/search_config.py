"""
Sistema de configuração dinâmica para múltiplos provedores de busca.
Suporta SearXNG, Tavily, Google Custom Search API e SerpAPI.
"""

import os
import requests
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class SearchProvider(Enum):
    """Provedores de busca suportados"""
    SEARXNG = "searxng"
    TAVILY = "tavily"
    GOOGLE = "google"
    SERPAPI = "serpapi"

@dataclass
class SearchConfig:
    """Configuração para um provedor de busca"""
    provider: SearchProvider
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    timeout: int = 10
    max_results: int = 10
    language: str = "pt-BR"
    safe_search: int = 0

class SearchConfigManager:
    """Gerenciador de configurações para múltiplos provedores de busca"""
    
    def __init__(self):
        self.configs: Dict[SearchProvider, SearchConfig] = {}
        self.default_provider = self._get_default_provider()
        self._load_configurations()
    
    def _get_default_provider(self) -> SearchProvider:
        """Determina o provedor padrão baseado nas variáveis de ambiente"""
        default_search = os.getenv('DEFAULT_SEARCH_PROVIDER', 'searxng').lower()
        
        try:
            return SearchProvider(default_search)
        except ValueError:
            logger.warning(f"Provedor de busca '{default_search}' não suportado. Usando SearXNG como padrão.")
            return SearchProvider.SEARXNG
    
    def _load_configurations(self):
        """Carrega configurações de todos os provedores disponíveis"""
        for provider in SearchProvider:
            config = self._load_provider_config(provider)
            if config:
                self.configs[provider] = config
                logger.info(f"Configuração de busca carregada para {provider.value}")
    
    def _load_provider_config(self, provider: SearchProvider) -> Optional[SearchConfig]:
        """Carrega configuração para um provedor específico"""
        if provider == SearchProvider.SEARXNG:
            base_url = os.getenv('SEARXNG_URL', 'http://localhost:8080')
            api_key = os.getenv('SEARXNG_API_KEY')  # Opcional
            timeout = int(os.getenv('SEARXNG_TIMEOUT', '30'))
            language = os.getenv('SEARXNG_LANGUAGE', 'pt-BR')
            safe_search = int(os.getenv('SEARXNG_SAFE_SEARCH', '0'))
            max_results = int(os.getenv('MAX_SEARCH_RESULTS', '10'))
            
            return SearchConfig(
                provider=provider,
                base_url=base_url,
                api_key=api_key,
                timeout=timeout,
                max_results=max_results,
                language=language,
                safe_search=safe_search
            )
        
        elif provider == SearchProvider.GOOGLE:
            api_key = os.getenv('GOOGLE_API_KEY')
            cse_id = os.getenv('GOOGLE_CSE_ID')
            
            if not api_key or not cse_id:
                logger.debug("Google Search API não configurado (API key ou CSE ID ausente)")
                return None
            
            timeout = int(os.getenv('GOOGLE_TIMEOUT', '10'))
            max_results = int(os.getenv('GOOGLE_MAX_RESULTS', '10'))
            
            return SearchConfig(
                provider=provider,
                api_key=api_key,
                base_url=f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}",
                timeout=timeout,
                max_results=max_results
            )
        
        elif provider == SearchProvider.TAVILY:
            api_key = os.getenv('TAVILY_API_KEY')
            
            if not api_key:
                logger.debug("Tavily não configurado (API key ausente)")
                return None
            
            timeout = int(os.getenv('TAVILY_TIMEOUT', '10'))
            max_results = int(os.getenv('TAVILY_MAX_RESULTS', '10'))
            
            return SearchConfig(
                provider=provider,
                api_key=api_key,
                base_url="https://api.tavily.com/search",
                timeout=timeout,
                max_results=max_results
            )
        
        elif provider == SearchProvider.SERPAPI:
            api_key = os.getenv('SERPAPI_KEY')
            
            if not api_key:
                logger.debug("SerpAPI não configurado (API key ausente)")
                return None
            
            timeout = int(os.getenv('SERPAPI_TIMEOUT', '10'))
            max_results = int(os.getenv('SERPAPI_MAX_RESULTS', '10'))
            
            return SearchConfig(
                provider=provider,
                api_key=api_key,
                base_url="https://serpapi.com/search",
                timeout=timeout,
                max_results=max_results
            )
        
        return None
    
    def get_config(self, provider: Optional[SearchProvider] = None) -> SearchConfig:
        """Obtém configuração para um provedor específico ou o padrão"""
        if provider is None:
            provider = self.default_provider
        
        if provider not in self.configs:
            # Tenta usar o próximo provedor disponível
            available = self.get_available_providers()
            if available:
                provider = available[0]
                logger.warning(f"Provedor padrão não disponível, usando {provider.value}")
            else:
                raise ValueError("Nenhum provedor de busca configurado")
        
        return self.configs[provider]
    
    def get_available_providers(self) -> List[SearchProvider]:
        """Retorna lista de provedores disponíveis"""
        return list(self.configs.keys())
    
    def is_provider_available(self, provider: SearchProvider) -> bool:
        """Verifica se um provedor está disponível"""
        return provider in self.configs
    
    def search(self, query: str, provider: Optional[SearchProvider] = None, **kwargs) -> List[Dict[str, Any]]:
        """Executa busca usando o provedor especificado ou padrão"""
        config = self.get_config(provider)
        
        try:
            if config.provider == SearchProvider.SEARXNG:
                return self._search_with_searxng(query, config, **kwargs)
            elif config.provider == SearchProvider.TAVILY:
                return self._search_with_tavily(query, config, **kwargs)
            elif config.provider == SearchProvider.GOOGLE:
                return self._search_with_google(query, config, **kwargs)
            elif config.provider == SearchProvider.SERPAPI:
                return self._search_with_serpapi(query, config, **kwargs)
            else:
                raise ValueError(f"Provedor {config.provider.value} não implementado")
        
        except Exception as e:
            logger.error(f"Erro na busca com {config.provider.value}: {e}")
            
            # Tenta usar um provedor alternativo
            available = [p for p in self.get_available_providers() if p != config.provider]
            if available:
                logger.info(f"Tentando busca com provedor alternativo: {available[0].value}")
                return self.search(query, available[0], **kwargs)
            
            raise
    
    def _search_with_searxng(self, query: str, config: SearchConfig, **kwargs) -> List[Dict[str, Any]]:
        """Busca usando SearXNG"""
        search_url = f"{config.base_url}/search"
        
        params = {
            'q': query,
            'format': 'json',
            'categories': 'general,news',
            'language': config.language,
            'safesearch': config.safe_search
        }
        
        headers = {}
        if config.api_key:
            headers['Authorization'] = f"Bearer {config.api_key}"
        
        response = requests.get(search_url, params=params, headers=headers, timeout=config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('results', [])[:config.max_results]:
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'snippet': item.get('content', ''),
                'source': 'searxng'
            })
        
        return results
    
    def _search_with_google(self, query: str, config: SearchConfig, **kwargs) -> List[Dict[str, Any]]:
        """Busca usando Google Custom Search API"""
        params = {
            'q': query,
            'num': min(config.max_results, 10),  # Google limita a 10
            'hl': 'pt-BR',
            'gl': 'br'
        }
        
        response = requests.get(config.base_url, params=params, timeout=config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('items', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'google'
            })
        
        return results
    
    def _search_with_serpapi(self, query: str, config: SearchConfig, **kwargs) -> List[Dict[str, Any]]:
        """Busca usando SerpAPI"""
        params = {
            'q': query,
            'api_key': config.api_key,
            'engine': 'google',
            'num': config.max_results,
            'hl': 'pt',
            'gl': 'br'
        }
        
        response = requests.get(config.base_url, params=params, timeout=config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('organic_results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'serpapi'
            })
        
        return results
    
    def _search_with_tavily(self, query: str, config: SearchConfig, **kwargs) -> List[Dict[str, Any]]:
        """Busca usando Tavily"""
        headers = {
            'Authorization': f'Bearer {config.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'query': query,
            'search_depth': kwargs.get('search_depth', 'basic'),
            'include_answer': kwargs.get('include_answer', False),
            'include_raw_content': kwargs.get('include_raw_content', False),
            'max_results': config.max_results,
            'include_domains': kwargs.get('include_domains', []),
            'exclude_domains': kwargs.get('exclude_domains', [])
        }
        
        response = requests.post(config.base_url, json=payload, headers=headers, timeout=config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('url', ''),
                'snippet': item.get('content', ''),
                'score': item.get('score', 0),
                'raw_content': item.get('raw_content', ''),
                'source': 'tavily'
            })
        
        # Adiciona resposta do Tavily se disponível
        if data.get('answer'):
            results.insert(0, {
                'title': 'Tavily AI Answer',
                'url': '',
                'snippet': data.get('answer'),
                'score': 1.0,
                'source': 'tavily_answer'
            })
        
        return results

    def _search_with_serpapi(self, query: str, config: SearchConfig, **kwargs) -> List[Dict[str, Any]]:
        """Busca usando SerpAPI"""
        params = {
            'q': query,
            'api_key': config.api_key,
            'engine': 'google',
            'num': config.max_results,
            'hl': 'pt',
            'gl': 'br'
        }
        
        response = requests.get(config.base_url, params=params, timeout=config.timeout)
        response.raise_for_status()
        
        data = response.json()
        results = []
        
        for item in data.get('organic_results', []):
            results.append({
                'title': item.get('title', ''),
                'url': item.get('link', ''),
                'snippet': item.get('snippet', ''),
                'source': 'serpapi'
            })
        
        return results

# Instância global do gerenciador
search_manager = SearchConfigManager()

def search_internet(query: str, provider: Optional[SearchProvider] = None, **kwargs) -> List[Dict[str, Any]]:
    """Função de conveniência para busca na internet"""
    return search_manager.search(query, provider, **kwargs)

def list_available_search_providers() -> List[str]:
    """Lista provedores de busca disponíveis"""
    return [provider.value for provider in search_manager.get_available_providers()]
