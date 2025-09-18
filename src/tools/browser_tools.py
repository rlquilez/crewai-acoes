"""
Ferramentas para navegação web e scraping usando Browserless.
"""

import requests
import json
import os
from bs4 import BeautifulSoup
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import time
import logging
from urllib.parse import urljoin

logger = logging.getLogger(__name__)


class BrowserToolsInput(BaseModel):
    """Input schema para BrowserTools."""
    url: str = Field(..., description="URL do website para fazer scraping")
    max_words: int = Field(default=2000, description="Número máximo de palavras para resumir")


class BrowserTools:
    """Ferramentas para navegação web e scraping usando Browserless."""
    
    @staticmethod
    def scrape_and_summarize_website(url: str, max_words: int = 2000) -> str:
        """
        Faz scraping de um website usando Browserless e retorna um resumo do conteúdo.
        
        Args:
            url: URL do website
            max_words: Número máximo de palavras no resumo
            
        Returns:
            Resumo do conteúdo do website
        """
        try:
            # Tenta usar Browserless primeiro
            browserless_url = os.getenv('BROWSERLESS_URL')
            if browserless_url:
                content = BrowserTools._scrape_with_browserless(url)
                if content:
                    return BrowserTools._process_content(content, url, max_words)
            
            # Fallback para requests tradicional
            return BrowserTools._scrape_with_requests(url, max_words)
            
        except Exception as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return f"Erro ao acessar o website {url}: {str(e)}"

    @staticmethod
    def _scrape_with_browserless(url: str) -> Optional[str]:
        """
        Faz scraping usando Browserless.
        
        Args:
            url: URL para fazer scraping
            
        Returns:
            HTML content ou None se falhar
        """
        try:
            browserless_url = os.getenv('BROWSERLESS_URL')
            token = os.getenv('BROWSERLESS_TOKEN')
            timeout = int(os.getenv('BROWSERLESS_TIMEOUT', '30000'))
            block_ads = os.getenv('BROWSERLESS_BLOCK_ADS', 'true').lower() == 'true'
            stealth = os.getenv('BROWSERLESS_STEALTH', 'true').lower() == 'true'
            ignore_https = os.getenv('BROWSERLESS_IGNORE_HTTPS_ERRORS', 'true').lower() == 'true'
            
            # Endpoint do Browserless para conteúdo
            endpoint = urljoin(browserless_url, '/content')
            
            headers = {'Content-Type': 'application/json'}
            if token:
                headers['Authorization'] = f'Bearer {token}'
            
            payload = {
                'url': url,
                'options': {
                    'timeout': timeout,
                    'waitUntil': 'networkidle2',
                    'blockAds': block_ads,
                    'stealth': stealth,
                    'ignoreHTTPSErrors': ignore_https
                },
                'gotoOptions': {
                    'waitUntil': 'networkidle2',
                    'timeout': timeout
                }
            }
            
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=timeout/1000 + 10  # timeout em segundos + buffer
            )
            response.raise_for_status()
            
            return response.text
            
        except Exception as e:
            logger.error(f"Erro no Browserless para {url}: {e}")
            return None

    @staticmethod
    def _scrape_with_requests(url: str, max_words: int) -> str:
        """
        Fallback: scraping tradicional com requests.
        
        Args:
            url: URL do website
            max_words: Número máximo de palavras
            
        Returns:
            Conteúdo processado
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return BrowserTools._process_content(response.text, url, max_words)
            
        except Exception as e:
            logger.error(f"Erro no requests para {url}: {e}")
            raise

    @staticmethod
    def _process_content(html_content: str, url: str, max_words: int) -> str:
        """
        Processa o conteúdo HTML extraído.
        
        Args:
            html_content: HTML do website
            url: URL original
            max_words: Número máximo de palavras
            
        Returns:
            Conteúdo processado e resumido
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove scripts, styles e outros elementos desnecessários
            for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
                element.decompose()
            
            # Remove ads e elementos promocionais
            for element in soup.find_all(['div', 'section'], class_=lambda x: x and any(
                keyword in x.lower() for keyword in ['ad', 'advertisement', 'promo', 'banner', 'popup']
            )):
                element.decompose()
            
            # Extrai texto principal
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Remove linhas vazias e espaços excessivos
            lines = [line.strip() for line in text_content.split('\n') if line.strip()]
            text_content = ' '.join(lines)
            
            # Limita o número de palavras
            words = text_content.split()
            if len(words) > max_words:
                text_content = ' '.join(words[:max_words]) + '...'
            
            return f"Conteúdo extraído de {url}:\n\n{text_content}"
            
        except Exception as e:
            logger.error(f"Erro ao processar conteúdo de {url}: {e}")
            return f"Erro ao processar o conteúdo de {url}: {str(e)}"
            
            # Extrai o texto principal
            text_content = soup.get_text(separator=' ', strip=True)
            
            # Limita o número de palavras
            words = text_content.split()
            if len(words) > max_words:
                text_content = ' '.join(words[:max_words]) + '...'
            
            return f"Conteúdo extraído de {url}:\n\n{text_content}"
            
        except requests.RequestException as e:
            logger.error(f"Erro ao acessar {url}: {e}")
            return f"Erro ao acessar o website {url}: {str(e)}"
        except Exception as e:
            logger.error(f"Erro inesperado ao processar {url}: {e}")
            return f"Erro ao processar o website {url}: {str(e)}"

    @staticmethod
    def get_page_title(url: str) -> str:
        """
        Obtém o título de uma página web.
        
        Args:
            url: URL da página
            
        Returns:
            Título da página
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')
            
            return title.get_text(strip=True) if title else "Título não encontrado"
            
        except Exception as e:
            logger.error(f"Erro ao obter título de {url}: {e}")
            return f"Erro ao obter título: {str(e)}"

    @staticmethod
    def extract_links(url: str) -> list:
        """
        Extrai todos os links de uma página.
        
        Args:
            url: URL da página
            
        Returns:
            Lista de links encontrados
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            links = []
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True)
                if href.startswith('http'):
                    links.append({'url': href, 'text': text})
            
            return links[:20]  # Limita a 20 links
            
        except Exception as e:
            logger.error(f"Erro ao extrair links de {url}: {e}")
            return []
