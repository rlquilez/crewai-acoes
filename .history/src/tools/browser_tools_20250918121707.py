"""
Ferramentas para navegação web e scraping.
"""

import requests
from bs4 import BeautifulSoup
from typing import Dict, Any
from crewai_tools import BaseTool
from pydantic import BaseModel, Field
import time
import logging

logger = logging.getLogger(__name__)


class BrowserToolsInput(BaseModel):
    """Input schema para BrowserTools."""
    url: str = Field(..., description="URL do website para fazer scraping")
    max_words: int = Field(default=2000, description="Número máximo de palavras para resumir")


class BrowserTools:
    """Ferramentas para navegação web e scraping."""
    
    @staticmethod
    def scrape_and_summarize_website(url: str, max_words: int = 2000) -> str:
        """
        Faz scraping de um website e retorna um resumo do conteúdo.
        
        Args:
            url: URL do website
            max_words: Número máximo de palavras no resumo
            
        Returns:
            Resumo do conteúdo do website
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove scripts, styles e outros elementos desnecessários
            for element in soup(['script', 'style', 'nav', 'footer', 'aside']):
                element.decompose()
            
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
