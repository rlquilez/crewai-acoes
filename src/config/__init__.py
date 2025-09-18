"""
Sistema de configuração dinâmica central para CrewAI Stock Analysis.
Gerencia todos os provedores: LLM, Search, Financial Data.
"""

import os
import logging
from typing import Dict, Any, Optional, Union
from dataclasses import dataclass

# Importa gerenciadores específicos
from .llm_config import LLMConfigManager, LLMProvider
from .search_config import SearchConfigManager, SearchProvider
from .alpha_vantage_config import AlphaVantageManager

logger = logging.getLogger(__name__)

@dataclass
class AppConfig:
    """Configuração geral da aplicação"""
    name: str = "CrewAI Stock Analysis"
    version: str = "2.0.0"
    environment: str = "production"
    debug: bool = False
    log_level: str = "INFO"
    cache_enabled: bool = True
    cache_ttl: int = 3600
    max_execution_time: int = 300
    memory_limit: bool = True

class ConfigManager:
    """Gerenciador central de todas as configurações"""
    
    def __init__(self):
        self.app_config = self._load_app_config()
        self.llm_manager = LLMConfigManager()
        self.search_manager = SearchConfigManager()
        self.alpha_vantage_manager = AlphaVantageManager()
        
        self._setup_logging()
        self._log_configuration_status()
    
    def _load_app_config(self) -> AppConfig:
        """Carrega configurações gerais da aplicação"""
        return AppConfig(
            name=os.getenv('APP_NAME', 'CrewAI Stock Analysis'),
            version=os.getenv('APP_VERSION', '2.0.0'),
            environment=os.getenv('APP_ENVIRONMENT', 'production'),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            cache_enabled=os.getenv('CACHE_ENABLED', 'true').lower() == 'true',
            cache_ttl=int(os.getenv('CACHE_TTL', '3600')),
            max_execution_time=int(os.getenv('MAX_EXECUTION_TIME', '300')),
            memory_limit=os.getenv('MEMORY_LIMIT', 'true').lower() == 'true'
        )
    
    def _setup_logging(self):
        """Configura sistema de logging"""
        log_level = getattr(logging, self.app_config.log_level.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        if self.app_config.debug:
            logging.getLogger().setLevel(logging.DEBUG)
    
    def _log_configuration_status(self):
        """Registra status das configurações no log"""
        logger.info(f"=== {self.app_config.name} v{self.app_config.version} ===")
        logger.info(f"Environment: {self.app_config.environment}")
        logger.info(f"Debug: {self.app_config.debug}")
        
        # Status LLM
        available_llms = self.llm_manager.get_available_providers()
        logger.info(f"LLM Providers: {[p.value for p in available_llms]}")
        logger.info(f"Default LLM: {self.llm_manager.default_provider.value}")
        
        # Status Search
        available_search = self.search_manager.get_available_providers()
        logger.info(f"Search Providers: {[p.value for p in available_search]}")
        logger.info(f"Default Search: {self.search_manager.default_provider.value}")
        
        # Status Alpha Vantage
        av_status = "enabled" if self.alpha_vantage_manager.is_available() else "disabled"
        logger.info(f"Alpha Vantage: {av_status}")
        
        if self.alpha_vantage_manager.config.premium:
            logger.info("Alpha Vantage Premium: enabled")
    
    def get_llm(self, provider: Optional[Union[LLMProvider, str]] = None):
        """Obtém instância de LLM configurada"""
        return self.llm_manager.get_crewai_llm(provider)
    
    def search_internet(self, query: str, provider: Optional[SearchProvider] = None):
        """Executa busca na internet"""
        return self.search_manager.search(query, provider)
    
    def get_financial_data(self, symbol: str) -> Dict[str, Any]:
        """
        Obtém dados financeiros combinados (Yahoo Finance + Alpha Vantage)
        """
        financial_data = {
            'symbol': symbol,
            'yahoo_finance': True,  # Sempre disponível
            'alpha_vantage': False
        }
        
        # Dados do Alpha Vantage (se disponível)
        if self.alpha_vantage_manager.is_available():
            av_data = self.alpha_vantage_manager.get_enhanced_financial_data(symbol)
            if av_data.get('alpha_vantage_available'):
                financial_data['alpha_vantage'] = True
                financial_data['alpha_vantage_data'] = av_data
                
                # Contexto MCP
                mcp_context = self.alpha_vantage_manager.get_mcp_context(symbol)
                if mcp_context:
                    financial_data['mcp_context'] = mcp_context
        
        return financial_data
    
    def get_configuration_summary(self) -> Dict[str, Any]:
        """Retorna resumo de todas as configurações"""
        return {
            'app': {
                'name': self.app_config.name,
                'version': self.app_config.version,
                'environment': self.app_config.environment,
                'debug': self.app_config.debug
            },
            'llm': {
                'available_providers': [p.value for p in self.llm_manager.get_available_providers()],
                'default_provider': self.llm_manager.default_provider.value
            },
            'search': {
                'available_providers': [p.value for p in self.search_manager.get_available_providers()],
                'default_provider': self.search_manager.default_provider.value
            },
            'financial_data': {
                'yahoo_finance': True,
                'alpha_vantage': self.alpha_vantage_manager.is_available(),
                'alpha_vantage_premium': self.alpha_vantage_manager.config.premium if self.alpha_vantage_manager.is_available() else False
            },
            'features': {
                'cache_enabled': self.app_config.cache_enabled,
                'memory_limit': self.app_config.memory_limit,
                'max_execution_time': self.app_config.max_execution_time
            }
        }
    
    def validate_configuration(self) -> Dict[str, Any]:
        """Valida todas as configurações e retorna status"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        # Valida LLM
        if not self.llm_manager.get_available_providers():
            validation['valid'] = False
            validation['errors'].append("Nenhum provedor de LLM configurado")
        
        # Valida Search
        if not self.search_manager.get_available_providers():
            validation['warnings'].append("Nenhum provedor de busca configurado")
        
        # Valida configurações críticas
        if not any(self.llm_manager.is_provider_available(p) for p in [LLMProvider.OPENAI, LLMProvider.ANTHROPIC]):
            validation['warnings'].append("Nenhum provedor de LLM principal (OpenAI/Anthropic) configurado")
        
        return validation
    
    def get_provider_recommendations(self) -> Dict[str, str]:
        """Retorna recomendações de configuração"""
        recommendations = {}
        
        # LLM
        if not self.llm_manager.is_provider_available(LLMProvider.OPENAI):
            recommendations['openai'] = "Configure OPENAI_API_KEY para melhor performance geral"
        
        if not self.llm_manager.is_provider_available(LLMProvider.ANTHROPIC):
            recommendations['anthropic'] = "Configure ANTHROPIC_API_KEY para análises mais detalhadas"
        
        # Search
        if not self.search_manager.is_provider_available(SearchProvider.GOOGLE):
            recommendations['google_search'] = "Configure Google Search API como fallback robusto"
        
        # Alpha Vantage
        if not self.alpha_vantage_manager.is_available():
            recommendations['alpha_vantage'] = "Configure Alpha Vantage para dados financeiros mais completos"
        
        return recommendations

# Instância global do gerenciador
config_manager = ConfigManager()

# Funções de conveniência para acesso global
def get_llm(provider: Optional[Union[LLMProvider, str]] = None):
    """Obtém LLM configurado"""
    return config_manager.get_llm(provider)

def search_internet(query: str, provider: Optional[SearchProvider] = None):
    """Busca na internet"""
    return config_manager.search_internet(query, provider)

def get_financial_data(symbol: str):
    """Obtém dados financeiros"""
    return config_manager.get_financial_data(symbol)

def get_config_summary():
    """Obtém resumo das configurações"""
    return config_manager.get_configuration_summary()

def validate_config():
    """Valida configurações"""
    return config_manager.validate_configuration()
