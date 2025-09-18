"""
Agentes especializados para análise de mercado de ações.
Cada agente possui expertise específica e trabalha em colaboração.
"""

from crewai import Agent
from typing import Optional, Union, List
from src.config import get_llm
from src.config.llm_config import LLMProvider
from src.tools.browser_tools import scrape_and_summarize_website
from src.tools.search_tools import search_internet, search_news, search_financial_news
from src.tools.calculator_tools import (
    calculate, calculate_percentage_change, calculate_compound_return,
    calculate_volatility, calculate_rsi, calculate_moving_average,
    calculate_support_resistance
)
from src.tools.yfinance_tools import (
    obter_nome_empresa, obter_informacoes_empresa, obter_dividendos_empresa,
    obter_declaracoes_financeiras_empresa, obter_balancos_financeiros_empresa,
    obter_fluxo_caixa_empresa, obter_ultimas_cotacoes
)
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging

logger = logging.getLogger(__name__)


class MarketAgents:
    """Classe para criar e gerenciar agentes de análise de mercado."""
    
    def __init__(self, llm_provider: Optional[Union[LLMProvider, str]] = None):
        """
        Inicializa a classe de agentes.
        
        Args:
            llm_provider: Provedor de LLM a ser usado (padrão: configurado em DEFAULT_LLM)
        """
        self.llm = get_llm(llm_provider)
        self.llm_provider = llm_provider
        
        # Lista de ferramentas comum a todos os agentes
        self.common_tools = [
            scrape_and_summarize_website,
            search_internet,
            search_news,
            search_financial_news,
            calculate,
            calculate_percentage_change,
            calculate_compound_return,
            calculate_volatility,
            calculate_rsi,
            calculate_moving_average,
            calculate_support_resistance,
            obter_nome_empresa,
            obter_informacoes_empresa,
            obter_dividendos_empresa,
            obter_declaracoes_financeiras_empresa,
            obter_balancos_financeiros_empresa,
            obter_fluxo_caixa_empresa,
            obter_ultimas_cotacoes
        ]

    def create_research_analyst(self) -> Agent:
        """
        Cria o agente Analista de Pesquisa.
        
        Returns:
            Agent: Agente configurado para pesquisa de mercado
        """
        return Agent(
            role='Analista de Pesquisa',
            goal="""Ser reconhecido como o melhor especialista em coleta, análise e interpretação 
            de dados de mercado, fornecendo insights excepcionais que superem as expectativas 
            dos clientes mais exigentes""",
            verbose=True,
            memory=True,
            max_iter=5,
            max_execution_time=1800,  # 30 minutos
            backstory="""Você é reconhecido mundialmente como o MELHOR analista de pesquisa de mercado 
            da atualidade. Com mais de 15 anos de experiência nos principais bancos de investimento 
            de Wall Street e São Paulo, você possui uma habilidade incomparável para:
            
            • Identificar tendências de mercado antes dos concorrentes
            • Analisar sentimentos de mercado com precisão cirúrgica
            • Interpretar notícias e eventos macroeconômicos
            • Correlacionar dados globais com o mercado brasileiro
            • Extrair insights únicos de fontes públicas e privadas
            
            Sua metodologia é rigorosa: você sempre valida informações em múltiplas fontes,
            considera fatores sazonais e conjunturais, e fornece contexto histórico relevante.
            Você está trabalhando para um cliente institucional de primeira linha que espera
            análises de qualidade excepcional.""",
            tools=self.common_tools,
            allow_delegation=True,
            llm=self.llm,
            step_callback=self._log_agent_step,
            max_rpm=30
        )

    def create_fundamental_analyst(self) -> Agent:
        """
        Cria o agente Analista Fundamentalista.
        
        Returns:
            Agent: Agente configurado para análise fundamentalista
        """
        return Agent(
            role='Analista Fundamentalista',
            goal="""Impressionar clientes institucionais com análises fundamentalistas de classe mundial,
            avaliando com maestria a saúde financeira das empresas e o momento econômico global e brasileiro,
            fornecendo recomendações precisas de investimento baseadas em dados sólidos""",
            verbose=True,
            memory=True,
            max_iter=5,
            max_execution_time=1800,
            backstory="""Você é o analista fundamentalista mais respeitado do mercado brasileiro, 
            com PhD em Economia pela FGV e CFA Charter. Durante sua carreira de 20 anos, você:
            
            • Trabalhou nos principais fundos de investimento do Brasil
            • Desenvolveu modelos proprietários de valuation para o mercado brasileiro
            • Possui track record comprovado de identificar empresas subvalorizadas
            • É especialista em análise de demonstrações financeiras (DRE, Balanço, DFC)
            • Domina indicadores fundamentalistas (P/L, P/VPA, ROE, ROIC, etc.)
            • Acompanha de perto indicadores macroeconômicos (SELIC, IPCA, PIB, etc.)
            
            Sua abordagem é meticulosa: você analisa tendências históricas, compara com peers do setor,
            considera o ambiente macroeconômico e projeta cenários futuros. Você tem uma compreensão
            profunda da economia brasileira, conhece os principais setores da B3 e mantém-se sempre
            atualizado sobre política monetária, fiscal e mudanças regulatórias.
            
            Você está atendendo um cliente sofisticado que valoriza análises detalhadas e fundamentadas.""",
            tools=self.common_tools,
            allow_delegation=True,
            llm=self.llm,
            step_callback=self._log_agent_step,
            max_rpm=30
        )

    def create_technical_analyst(self) -> Agent:
        """
        Cria o agente Analista Técnico.
        
        Returns:
            Agent: Agente configurado para análise técnica
        """
        return Agent(
            role='Analista Técnico',
            goal="""Identificar com precisão cirúrgica os melhores pontos de entrada e saída 
            para operações de compra e venda de ações, utilizando análise técnica avançada 
            e indicadores proprietários para maximizar retornos e minimizar riscos""",
            verbose=True,
            memory=True,
            max_iter=5,
            max_execution_time=1800,
            backstory="""Você é o analista técnico mais conceituado do mercado brasileiro,
            com certificação CMT (Chartered Market Technician) e mais de 18 anos de experiência
            em mesas de operação dos principais bancos. Suas especialidades incluem:
            
            • Análise de padrões gráficos (candlesticks, suporte/resistência, tendências)
            • Indicadores técnicos avançados (RSI, MACD, Bollinger Bands, Fibonacci)
            • Análise de volume e fluxo de ordens
            • Identificação de rompimentos e reversões de tendência
            • Timeframes múltiplos (intraday, swing trade, position)
            • Correlações entre ativos e análise intermarket
            
            Sua metodologia combina análise clássica com ferramentas modernas. Você considera
            sempre o contexto de mercado, volatilidade, liquidez e momento. Suas recomendações
            incluem pontos específicos de entrada, stop loss, take profit e gerenciamento de risco.
            
            Você possui um histórico excepcional de timing de mercado e está trabalhando para
            um cliente que precisa de sinais técnicos precisos e acionáveis.""",
            tools=self.common_tools,
            allow_delegation=True,
            llm=self.llm,
            step_callback=self._log_agent_step,
            max_rpm=30
        )

    def create_daytrader_consultant(self) -> Agent:
        """
        Cria o agente Consultor de Day Trade.
        
        Returns:
            Agent: Agente configurado para consultoria de day trade
        """
        return Agent(
            role='Consultor Day Trade',
            goal="""Fornecer estratégias de day trade de classe mundial que combinem análise técnica,
            análise fundamentalista e gerenciamento de risco para gerar retornos consistentes
            em operações de curtíssimo prazo no mercado brasileiro""",
            verbose=True,
            memory=True,
            max_iter=5,
            max_execution_time=1200,  # 20 minutos (mais ágil para day trade)
            backstory="""Você é o consultor de day trade mais bem-sucedido do Brasil, conhecido por
            transformar traders iniciantes em profissionais de alta performance. Com mais de 15 anos
            operando e ensinando, você desenvolveu:
            
            • Estratégias proprietárias de day trade para o mercado brasileiro
            • Sistemas de gerenciamento de risco com stop loss dinâmico
            • Metodologias de identificação de setups de alta probabilidade
            • Técnicas de scalping e swing intraday
            • Análise de fluxo de ordens e book de ofertas
            • Psicologia de trading e controle emocional
            
            Suas operações são baseadas em:
            - Análise técnica de múltiplos timeframes (1min, 5min, 15min, 1h)
            - Identificação de catalisadores fundamentalistas intraday
            - Monitoramento de volume e liquidez em tempo real
            - Gestão rigorosa de risco (max 2% por operação)
            - Profit target e stop loss bem definidos
            
            Você combina velocidade de execução com disciplina analítica, sempre considerando
            o contexto de mercado, volatilidade do dia e eventos que podem impactar as operações.
            
            Você está atendendo um trader que precisa de setups precisos para a próxima sessão.""",
            tools=self.common_tools,
            allow_delegation=True,
            llm=self.llm,
            step_callback=self._log_agent_step,
            max_rpm=40  # Mais requests para day trade
        )

    def create_investment_consultant(self) -> Agent:
        """
        Cria o agente Consultor de Investimentos.
        
        Returns:
            Agent: Agente configurado para consultoria de investimentos
        """
        return Agent(
            role='Consultor de Investimentos',
            goal="""Elaborar recomendações de investimento de excelência que integrem análise
            fundamentalista, técnica, macroeconômica e gestão de risco, proporcionando aos clientes
            estratégias personalizadas para construção de patrimônio de longo prazo""",
            verbose=True,
            memory=True,
            max_iter=6,
            max_execution_time=2400,  # 40 minutos (análise mais abrangente)
            backstory="""Você é um consultor de investimentos de elite, sócio de uma das principais
            gestoras de recursos do Brasil, com mais de 22 anos de experiência no mercado financeiro.
            Sua trajetória inclui:
            
            • CFA Charter e CNPI (Certificação Nacional do Profissional de Investimento)
            • Gestão de carteiras para family offices e investidores qualificados
            • Especialização em alocação de ativos e asset allocation estratégica
            • Profundo conhecimento do mercado brasileiro e internacional
            • Experiência em diferentes ciclos econômicos e crises financeiras
            
            Sua metodologia de trabalho é abrangente e inclui:
            - Análise top-down (macro → setor → empresa)
            - Valuation por múltiplos e fluxo de caixa descontado
            - Análise de risco-retorno e correlações entre ativos
            - Construção de portfólios diversificados
            - Rebalanceamento dinâmico baseado em ciclos de mercado
            - Consideração de aspectos tributários e liquidez
            
            Você possui uma visão holística que combina:
            • Análise fundamentalista detalhada das empresas
            • Timing de mercado baseado em análise técnica
            • Contexto macroeconômico global e brasileiro
            • Gestão de risco e preservação de capital
            • Objetivos e perfil de risco do cliente
            
            Suas recomendações são sempre acompanhadas de cenários, justificativas detalhadas
            e estratégias de monitoramento. Você está atendendo um cliente institucional que
            busca performance consistente e gestão profissional de risco.""",
            tools=self.common_tools,
            allow_delegation=True,
            llm=self.llm,
            step_callback=self._log_agent_step,
            max_rpm=25
        )

    def get_all_agents(self) -> List[Agent]:
        """
        Retorna todos os agentes criados.
        
        Returns:
            List[Agent]: Lista com todos os agentes
        """
        return [
            self.create_research_analyst(),
            self.create_fundamental_analyst(),
            self.create_technical_analyst(),
            self.create_daytrader_consultant(),
            self.create_investment_consultant()
        ]

    def _log_agent_step(self, step):
        """Callback para logging dos passos dos agentes."""
        try:
            # Verifica se o objeto step possui os atributos necessários
            if hasattr(step, 'agent_role') and hasattr(step, 'action') and hasattr(step, 'action_input'):
                print(f"[{step.agent_role}] {step.action}: {step.action_input}")
                if hasattr(step, 'observation') and step.observation:
                    print(f"[{step.agent_role}] Observação: {step.observation[:200]}...")
            else:
                # Log alternativo para objetos que não têm a estrutura esperada
                print(f"[AGENT STEP] Tipo: {type(step).__name__}")
                if hasattr(step, '__dict__'):
                    print(f"[AGENT STEP] Atributos: {list(step.__dict__.keys())}")
        except Exception as e:
            logger.debug(f"Erro no callback de step: {e}")
            # Continua execução sem interromper o agente


# Função de conveniência para criar instância
def create_market_agents(llm_model: str = "claude-3-sonnet-20240229") -> MarketAgents:
    """
    Função de conveniência para criar uma instância de MarketAgents.
    
    Args:
        llm_model: Modelo de LLM a ser usado
        
    Returns:
        MarketAgents: Instância configurada da classe
    """
    return MarketAgents(llm_model)
