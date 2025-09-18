"""
Sistema de configuração dinâmica para múltiplos provedores de LLM.
Suporta OpenAI, Anthropic, Deepseek, Grok e Ollama.
"""

import os
from typing import Optional, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Provedores de LLM suportados"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    DEEPSEEK = "deepseek"
    GROK = "grok"
    OLLAMA = "ollama"
    
    @classmethod
    def from_string(cls, value: str) -> 'LLMProvider':
        """Converte string para enum LLMProvider"""
        if isinstance(value, cls):
            return value
        
        # Tenta encontrar pelo valor
        for provider in cls:
            if provider.value == value.lower():
                return provider
        
        # Tenta encontrar pelo nome
        try:
            return cls[value.upper()]
        except KeyError:
            raise ValueError(f"Provedor '{value}' não é suportado. Provedores disponíveis: {', '.join([p.value for p in cls])}")

@dataclass
class LLMConfig:
    """Configuração para um provedor de LLM"""
    provider: LLMProvider
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    timeout: int = 120

class LLMConfigManager:
    """Gerenciador de configurações para múltiplos provedores de LLM"""
    
    # Modelos padrão para cada provedor
    DEFAULT_MODELS = {
        LLMProvider.OPENAI: "gpt-4o",  # Último modelo OpenAI
        LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",  # Último Claude
        LLMProvider.DEEPSEEK: "deepseek-reasoner",  # Modelo Reasoner
        LLMProvider.GROK: "grok-2-1212",  # Último Grok
        LLMProvider.OLLAMA: "llama3.2:latest"  # Modelo padrão Ollama
    }
    
    # URLs base padrão
    DEFAULT_BASE_URLS = {
        LLMProvider.OPENAI: "https://api.openai.com/v1",
        LLMProvider.ANTHROPIC: "https://api.anthropic.com",
        LLMProvider.DEEPSEEK: "https://api.deepseek.com/v1",
        LLMProvider.GROK: "https://api.x.ai/v1",
        LLMProvider.OLLAMA: "http://localhost:11434"
    }
    
    def __init__(self):
        self.configs: Dict[LLMProvider, LLMConfig] = {}
        self.default_provider = self._get_default_provider()
        self._load_configurations()
    
    def _get_default_provider(self) -> LLMProvider:
        """Determina o provedor padrão baseado nas variáveis de ambiente"""
        default_llm = os.getenv('DEFAULT_LLM', 'openai').lower()
        
        try:
            return LLMProvider(default_llm)
        except ValueError:
            logger.warning(f"Provedor '{default_llm}' não suportado. Usando OpenAI como padrão.")
            return LLMProvider.OPENAI
    
    def _load_configurations(self):
        """Carrega configurações de todos os provedores disponíveis"""
        for provider in LLMProvider:
            config = self._load_provider_config(provider)
            if config:
                self.configs[provider] = config
                logger.info(f"Configuração carregada para {provider.value}")
    
    def _load_provider_config(self, provider: LLMProvider) -> Optional[LLMConfig]:
        """Carrega configuração para um provedor específico"""
        provider_name = provider.value.upper()
        
        # Verifica se a API key está disponível (exceto para Ollama)
        if provider != LLMProvider.OLLAMA:
            api_key = os.getenv(f'{provider_name}_API_KEY')
            if not api_key:
                logger.debug(f"API key não encontrada para {provider.value}")
                return None
        else:
            api_key = None
        
        # Configurações específicas
        model = os.getenv(f'{provider_name}_MODEL', self.DEFAULT_MODELS[provider])
        base_url = os.getenv(f'{provider_name}_BASE_URL', self.DEFAULT_BASE_URLS[provider])
        temperature = float(os.getenv(f'{provider_name}_TEMPERATURE', '0.1'))
        max_tokens = os.getenv(f'{provider_name}_MAX_TOKENS')
        timeout = int(os.getenv(f'{provider_name}_TIMEOUT', '120'))
        
        if max_tokens:
            max_tokens = int(max_tokens)
        
        return LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
    
    def get_config(self, provider: Optional[Union[LLMProvider, str]] = None) -> LLMConfig:
        """Obtém configuração para um provedor específico ou o padrão"""
        if provider is None:
            provider = self.default_provider
        elif isinstance(provider, str):
            try:
                provider = LLMProvider.from_string(provider)
            except ValueError as e:
                logger.error(f"Erro ao converter provider '{provider}': {e}")
                provider = self.default_provider
        
        if provider not in self.configs:
            raise ValueError(f"Provedor {provider.value} não está configurado ou disponível")
        
        return self.configs[provider]
    
    def get_available_providers(self) -> list[LLMProvider]:
        """Retorna lista de provedores disponíveis"""
        return list(self.configs.keys())
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Verifica se um provedor está disponível"""
        return provider in self.configs
    
    def get_crewai_llm(self, provider: Optional[Union[LLMProvider, str]] = None):
        """Retorna instância de LLM configurada para CrewAI"""
        config = self.get_config(provider)
        
        try:
            if config.provider == LLMProvider.OPENAI:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=config.model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.ANTHROPIC:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=config.model,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.DEEPSEEK:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=config.model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.GROK:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=config.model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.OLLAMA:
                from langchain_ollama import ChatOllama
                return ChatOllama(
                    model=config.model,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    timeout=config.timeout
                )
            
            else:
                raise ValueError(f"Provedor {config.provider.value} não implementado")
                
        except ImportError as e:
            logger.error(f"Biblioteca necessária não instalada para {config.provider.value}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao configurar LLM {config.provider.value}: {e}")
            raise

# Instância global do gerenciador
llm_manager = LLMConfigManager()

def get_default_llm():
    """Função de conveniência para obter o LLM padrão"""
    return llm_manager.get_crewai_llm()

def get_llm(provider: LLMProvider):
    """Função de conveniência para obter um LLM específico"""
    return llm_manager.get_crewai_llm(provider)

def list_available_llms() -> list[str]:
    """Lista provedores de LLM disponíveis"""
    return [provider.value for provider in llm_manager.get_available_providers()]
