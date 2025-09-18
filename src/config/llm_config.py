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
        LLMProvider.DEEPSEEK: "deepseek-reasoner",  # Modelo Reasoner (será corrigido automaticamente)
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
        logger.info(f"DEFAULT_LLM encontrado: {default_llm}")
        
        try:
            provider = LLMProvider(default_llm)
            logger.info(f"Provedor padrão configurado: {provider.value}")
            return provider
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
        logger.info(f"Modelo original carregado para {provider.value}: {model}")
        
        # Correção para modelos DeepSeek sem prefixo correto
        if provider == LLMProvider.DEEPSEEK and model and not model.startswith("deepseek/"):
            original_model = model
            model = f"deepseek/{model}"
            logger.info(f"Modelo DeepSeek corrigido durante carregamento: {original_model} -> {model}")
        
        base_url = os.getenv(f'{provider_name}_BASE_URL', self.DEFAULT_BASE_URLS[provider])
        temperature = float(os.getenv(f'{provider_name}_TEMPERATURE', '0.1'))
        max_tokens = os.getenv(f'{provider_name}_MAX_TOKENS')
        timeout = int(os.getenv(f'{provider_name}_TIMEOUT', '120'))
        
        if max_tokens:
            max_tokens = int(max_tokens)
        
        config = LLMConfig(
            provider=provider,
            model=model,
            api_key=api_key,
            base_url=base_url,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout=timeout
        )
        
        logger.info(f"Configuração criada para {provider.value}: model={config.model}, api_key={'***' if config.api_key else 'None'}")
        return config
    
    def get_config(self, provider: Optional[Union[LLMProvider, str]] = None) -> LLMConfig:
        """Obtém configuração para um provedor específico ou o padrão"""
        if provider is None:
            provider = self.default_provider
            logger.info(f"Usando provedor padrão: {provider.value}")
        elif isinstance(provider, str):
            try:
                provider = LLMProvider.from_string(provider)
                logger.info(f"Provedor convertido de string: {provider.value}")
            except ValueError as e:
                logger.error(f"Erro ao converter provider '{provider}': {e}")
                provider = self.default_provider
                logger.warning(f"Usando provedor padrão como fallback: {provider.value}")
        
        logger.info(f"Tentando obter configuração para provedor: {provider.value}")
        logger.info(f"Provedores configurados: {[p.value for p in self.configs.keys()]}")
        
        if provider not in self.configs:
            error_msg = f"Provedor {provider.value} não está configurado ou disponível"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        config = self.configs[provider]
        logger.info(f"Configuração obtida para {provider.value}: model={config.model}")
        return config
    
    def get_available_providers(self) -> list[LLMProvider]:
        """Retorna lista de provedores disponíveis"""
        return list(self.configs.keys())
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Verifica se um provedor está disponível"""
        return provider in self.configs
    
    def _validate_model_format(self, config: LLMConfig) -> str:
        """Valida e corrige o formato do modelo para compatibilidade com LiteL LM"""
        model = config.model
        original_model = model
        
        # Para DeepSeek, garante que o modelo tenha o prefixo correto
        if config.provider == LLMProvider.DEEPSEEK:
            if not model.startswith("deepseek/"):
                model = f"deepseek/{model}"
                logger.info(f"Modelo DeepSeek corrigido: {original_model} -> {model}")
            else:
                logger.info(f"Modelo DeepSeek já no formato correto: {model}")
        
        # Para Grok, garante que o modelo tenha o prefixo correto
        elif config.provider == LLMProvider.GROK:
            if not model.startswith("grok"):
                model = f"grok-{model}"
                logger.info(f"Modelo Grok corrigido: {original_model} -> {model}")
        
        logger.info(f"Modelo final a ser usado: {model}")
        return model
    
    def get_crewai_llm(self, provider: Optional[Union[LLMProvider, str]] = None):
        """Retorna instância de LLM configurada para CrewAI"""
        config = self.get_config(provider)
        
        # Valida e corrige o formato do modelo
        validated_model = self._validate_model_format(config)
        
        try:
            if config.provider == LLMProvider.OPENAI:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=validated_model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.ANTHROPIC:
                from langchain_anthropic import ChatAnthropic
                return ChatAnthropic(
                    model=validated_model,
                    api_key=config.api_key,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.DEEPSEEK:
                from langchain_openai import ChatOpenAI
                logger.info(f"Criando LLM Deepseek com modelo: {validated_model}")
                logger.info(f"Base URL: {config.base_url}")
                logger.info(f"API Key presente: {'***' if config.api_key else 'NÃO'}")
                
                llm = ChatOpenAI(
                    model=validated_model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
                logger.info(f"LLM Deepseek criado com sucesso: {type(llm).__name__}")
                return llm
            
            elif config.provider == LLMProvider.GROK:
                from langchain_openai import ChatOpenAI
                return ChatOpenAI(
                    model=validated_model,
                    api_key=config.api_key,
                    base_url=config.base_url,
                    temperature=config.temperature,
                    max_tokens=config.max_tokens,
                    timeout=config.timeout
                )
            
            elif config.provider == LLMProvider.OLLAMA:
                from langchain_ollama import ChatOllama
                return ChatOllama(
                    model=validated_model,
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
