"""
Tarefas especializadas para análise de mercado financeiro.
"""

from crewai import Task
from typing import Dict, Any, Optional
from datetime import datetime


class MarketTasks:
    """Classe para criar e gerenciar tarefas de análise de mercado."""
    
    def __init__(self):
        """Inicializa a classe de tarefas."""
        self.current_date = datetime.now().strftime("%d/%m/%Y")
    
    def create_research_task(self, symbol: str, agent) -> Task:
        """
        Cria tarefa de pesquisa de mercado.
        
        Args:
            symbol: Símbolo da ação a ser analisada
            agent: Agente responsável pela tarefa
            
        Returns:
            Task: Tarefa configurada para pesquisa
        """
        return Task(
            description=f"""Realizar pesquisa abrangente sobre a empresa {symbol}, incluindo:

            1. IDENTIFICAÇÃO DA EMPRESA:
               • Nome completo e setor de atuação
               • Principais produtos/serviços
               • Posição competitiva no mercado
               • Principais concorrentes

            2. ANÁLISE DE NOTÍCIAS E SENTIMENTO:
               • Últimas notícias relevantes (30 dias)
               • Análise de sentimento de mercado
               • Eventos corporativos recentes
               • Comunicados relevantes da empresa

            3. CONTEXTO MACROECONÔMICO:
               • Cenário econômico brasileiro atual
               • Impacto dos indicadores macro no setor
               • Tendências globais que afetam a empresa
               • Política monetária e fiscal

            4. ANÁLISE SETORIAL:
               • Performance do setor vs mercado
               • Tendências e desafios setoriais
               • Regulamentações relevantes
               • Oportunidades e ameaças

            5. DADOS PRELIMINARES:
               • Cotação atual e variação recente
               • Volume de negociação
               • Múltiplos básicos de mercado
               
            Organize as informações de forma estruturada e destaque os pontos mais relevantes
            para a análise subsequente pelos outros especialistas.
            
            Data da análise: {self.current_date}
            """,
            expected_output=f"""Relatório estruturado de pesquisa sobre {symbol} contendo:
            
            📊 RESUMO EXECUTIVO
            • Visão geral da empresa e setor
            • Principais destaques e preocupações
            • Contexto atual de mercado
            
            🏢 PERFIL DA EMPRESA
            • Informações corporativas detalhadas
            • Modelo de negócio e posicionamento
            • Principais produtos/segmentos
            
            📰 ANÁLISE DE NOTÍCIAS (30 dias)
            • Resumo das principais notícias
            • Análise de sentimento
            • Eventos corporativos relevantes
            
            🌍 CENÁRIO MACROECONÔMICO
            • Contexto econômico brasileiro
            • Impactos setoriais
            • Fatores de risco e oportunidade
            
            📈 DADOS PRELIMINARES DE MERCADO
            • Preço e variação atual
            • Volume e liquidez
            • Múltiplos básicos
            
            ⚡ PONTOS DE ATENÇÃO
            • Fatores críticos para monitoramento
            • Riscos identificados
            • Oportunidades potenciais
            
            Formato: Markdown com emojis e formatação clara""",
            agent=agent,
            context=[],
            output_file=f"reports/research_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

    def create_fundamental_analysis_task(self, symbol: str, agent, research_task: Task) -> Task:
        """
        Cria tarefa de análise fundamentalista.
        
        Args:
            symbol: Símbolo da ação
            agent: Agente responsável
            research_task: Tarefa de pesquisa prévia
            
        Returns:
            Task: Tarefa de análise fundamentalista
        """
        return Task(
            description=f"""Realizar análise fundamentalista completa da empresa {symbol}, baseando-se 
            na pesquisa inicial e incluindo:

            1. ANÁLISE FINANCEIRA DETALHADA:
               • Demonstração de Resultados (últimos 4 anos)
               • Balanço Patrimonial (últimos 4 anos)
               • Demonstração de Fluxo de Caixa (últimos 4 anos)
               • Evolução de receitas, margens e lucros
               • Qualidade dos resultados financeiros

            2. INDICADORES FUNDAMENTALISTAS:
               • Múltiplos de valuation (P/L, P/VPA, EV/EBITDA)
               • Indicadores de rentabilidade (ROE, ROA, ROIC)
               • Indicadores de endividamento (D/E, Liquidez)
               • Indicadores de eficiência operacional
               • Comparação com peers do setor

            3. ANÁLISE DE CRESCIMENTO:
               • Taxa de crescimento histórica (receitas/lucros)
               • Projeções de crescimento futuro
               • Drivers de crescimento identificados
               • Sustentabilidade do crescimento

            4. ANÁLISE DE DIVIDENDOS:
               • Histórico de distribuição de dividendos
               • Yield de dividendos atual e histórico
               • Política de dividendos da empresa
               • Capacidade de manutenção dos dividendos

            5. VALUATION E PREÇO JUSTO:
               • Modelos de valuation (DCF, múltiplos)
               • Preço-alvo baseado em fundamentos
               • Cenários otimista, base e pessimista
               • Margem de segurança atual

            6. FORÇAS E FRAQUEZAS:
               • Vantagens competitivas identificadas
               • Pontos fracos e vulnerabilidades
               • Posição financeira e solidez
               • Qualidade da gestão e governança

            Data da análise: {self.current_date}
            """,
            expected_output=f"""Análise fundamentalista abrangente de {symbol} incluindo:
            
            💼 RESUMO EXECUTIVO FUNDAMENTALISTA
            • Tese de investimento principal
            • Recomendação fundamentalista (Compra/Mantenha/Venda)
            • Preço-alvo e potencial de valorização
            • Principais riscos e catalisadores
            
            📊 ANÁLISE FINANCEIRA HISTÓRICA
            • Performance de receitas, margens e lucros (4 anos)
            • Evolução dos indicadores de rentabilidade
            • Análise da estrutura de capital
            • Qualidade e consistência dos resultados
            
            🔢 INDICADORES FUNDAMENTALISTAS
            • Múltiplos de valuation vs peers
            • Indicadores de rentabilidade e eficiência
            • Métricas de endividamento e liquidez
            • Comparação setorial e histórica
            
            💰 ANÁLISE DE DIVIDENDOS
            • Histórico e sustentabilidade dos dividendos
            • Yield atual vs histórico vs setor
            • Política de dividendos e payout ratio
            • Projeção de dividendos futuros
            
            🎯 VALUATION E PREÇO JUSTO
            • Modelos de valuation aplicados
            • Preço-alvo em diferentes cenários
            • Margem de segurança atual
            • Sensibilidade às principais variáveis
            
            ⚖️ RISCOS E OPORTUNIDADES
            • Principais riscos fundamentalistas
            • Catalisadores de valor identificados
            • Vantagens competitivas sustentáveis
            • Fatores de monitoramento
            
            📈 RECOMENDAÇÃO FINAL
            • Rating fundamentalista
            • Horizonte de investimento recomendado
            • Estratégia de entrada/saída
            • Pontos de reavaliação
            
            Formato: Markdown detalhado com tabelas e gráficos quando aplicável""",
            agent=agent,
            context=[research_task],
            output_file=f"reports/fundamental_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

    def create_technical_analysis_task(self, symbol: str, agent, research_task: Task) -> Task:
        """
        Cria tarefa de análise técnica.
        
        Args:
            symbol: Símbolo da ação
            agent: Agente responsável
            research_task: Tarefa de pesquisa prévia
            
        Returns:
            Task: Tarefa de análise técnica
        """
        return Task(
            description=f"""Realizar análise técnica completa da ação {symbol}, incluindo:

            1. ANÁLISE DE TENDÊNCIA:
               • Identificação da tendência principal (primária, secundária, terciária)
               • Análise de múltiplos timeframes (diário, semanal, mensal)
               • Estrutura de topos e fundos
               • Rompimentos e confirmações de tendência

            2. SUPORTE E RESISTÊNCIA:
               • Níveis de suporte e resistência relevantes
               • Zonas de acumulação e distribuição
               • Níveis psicológicos importantes
               • Retrações de Fibonacci

            3. INDICADORES TÉCNICOS:
               • RSI (Relative Strength Index)
               • MACD (Moving Average Convergence Divergence)
               • Médias móveis (20, 50, 200 períodos)
               • Bandas de Bollinger
               • Volume e indicadores de volume

            4. PADRÕES GRÁFICOS:
               • Padrões de candlestick relevantes
               • Formações gráficas (triângulos, retângulos, etc.)
               • Gaps e suas implicações
               • Padrões de reversão ou continuação

            5. ANÁLISE DE VOLUME:
               • Volume médio vs volume atual
               • Divergências de volume
               • Volume nos rompimentos
               • Análise de fluxo de capital

            6. MOMENTUM E FORÇA RELATIVA:
               • Indicadores de momentum
               • Força relativa vs índice (IBOV)
               • Sinais de sobrecompra/sobrevenda
               • Divergências de momentum

            7. CENÁRIOS TÉCNICOS:
               • Cenário altista: alvos e estratégia
               • Cenário baixista: suportes e stops
               • Níveis de entrada ótimos
               • Gerenciamento de risco

            Data da análise: {self.current_date}
            """,
            expected_output=f"""Análise técnica detalhada de {symbol} contendo:
            
            🎯 RESUMO TÉCNICO EXECUTIVO
            • Bias técnico atual (Altista/Baixista/Neutro)
            • Recomendação técnica de curto/médio prazo
            • Principais níveis a monitorar
            • Setup de maior probabilidade
            
            📈 ANÁLISE DE TENDÊNCIA
            • Tendência em múltiplos timeframes
            • Estrutura técnica atual
            • Pontos de inflexão importantes
            • Confirmações e invalidações
            
            🎚️ NÍVEIS CRÍTICOS
            • Suportes e resistências principais
            • Zonas de decisão técnica
            • Retrações de Fibonacci relevantes
            • Níveis psicológicos importantes
            
            📊 INDICADORES TÉCNICOS
            • Análise dos principais indicadores
            • Sinais de entrada e saída
            • Divergências identificadas
            • Momentum e força relativa
            
            🕯️ PADRÕES GRÁFICOS
            • Formações técnicas identificadas
            • Padrões de candlestick relevantes
            • Implicações dos padrões
            • Alvos técnicos projetados
            
            📦 ANÁLISE DE VOLUME
            • Perfil de volume atual
            • Confirmações de movimento
            • Divergências de volume
            • Zonas de maior interesse
            
            🎪 CENÁRIOS TÉCNICOS
            • Cenário altista: entrada, alvo, stop
            • Cenário baixista: entrada, alvo, stop
            • Probabilidades de cada cenário
            • Estratégias de posicionamento
            
            ⚠️ GERENCIAMENTO DE RISCO
            • Níveis de stop loss sugeridos
            • Relação risco/retorno
            • Sizing de posição recomendado
            • Pontos de reavaliação
            
            Formato: Markdown com descrições técnicas claras e níveis específicos""",
            agent=agent,
            context=[research_task],
            output_file=f"reports/technical_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

    def create_daytrader_task(self, symbol: str, agent, research_task: Task, technical_task: Task) -> Task:
        """
        Cria tarefa de consultoria de day trade.
        
        Args:
            symbol: Símbolo da ação
            agent: Agente responsável
            research_task: Tarefa de pesquisa
            technical_task: Tarefa de análise técnica
            
        Returns:
            Task: Tarefa de day trade
        """
        return Task(
            description=f"""Desenvolver estratégia completa de day trade para {symbol} baseada em:

            1. SETUP DE DAY TRADE:
               • Identificação de setups de alta probabilidade
               • Análise de múltiplos timeframes (1min, 5min, 15min, 1h)
               • Confluências técnicas para entrada
               • Horários de maior volatilidade e volume

            2. ESTRATÉGIA DE ENTRADA:
               • Pontos ótimos de entrada (preço específico)
               • Confirmações necessárias antes da entrada
               • Volume mínimo para validar setup
               • Timing ideal para execução

            3. GERENCIAMENTO DE POSIÇÃO:
               • Stop loss técnico (valor específico)
               • Take profit primário e secundário
               • Trailing stop para maximizar ganhos
               • Sizing de posição baseado em risco

            4. ANÁLISE INTRADAY:
               • Padrões intraday recorrentes
               • Suporte e resistência intraday
               • Gap de abertura e suas implicações
               • Market makers e fluxo de ordens

            5. CATALISADORES DO DIA:
               • Eventos que podem impactar o preço
               • Horários de maior atenção
               • Notícias ou dados relevantes
               • Correlações com outros ativos

            6. PLANO DE EXECUÇÃO:
               • Pre-market: preparação e análise
               • Abertura: primeiros minutos
               • Meio do dia: oportunidades
               • Fechamento: estratégia de saída

            7. CENÁRIOS ALTERNATIVOS:
               • Plan B se setup principal falhar
               • Adaptação a diferentes condições de mercado
               • Gestão de drawdown intraday

            Data da operação: {self.current_date}
            Próxima sessão: Considerar abertura do próximo pregão
            """,
            expected_output=f"""Plano completo de day trade para {symbol} incluindo:
            
            ⚡ SETUP PRINCIPAL
            • Descrição do setup de maior probabilidade
            • Condições necessárias para ativação
            • Timeframe principal de operação
            • Confluências técnicas identificadas
            
            🎯 ESTRATÉGIA DE ENTRADA
            • Preço de entrada (valor específico)
            • Confirmações antes da execução
            • Volume mínimo necessário
            • Timing ideal (horário específico)
            
            🛡️ GERENCIAMENTO DE RISCO
            • Stop loss (valor exato)
            • Take profit 1 e 2 (valores específicos)
            • Tamanho da posição recomendado
            • Relação risco/retorno
            
            ⏰ CRONOGRAMA INTRADAY
            • 09:00-09:30: Análise de abertura
            • 09:30-11:00: Janela de maior oportunidade
            • 11:00-14:00: Monitoramento e ajustes
            • 14:00-17:00: Estratégia de fechamento
            
            📊 NÍVEIS INTRADAY CRÍTICOS
            • Suporte intraday: R$ XX,XX
            • Resistência intraday: R$ XX,XX
            • Zona de stop out: R$ XX,XX
            • Zona de realização: R$ XX,XX
            
            🚨 CATALISADORES E ALERTAS
            • Eventos do dia que podem impactar
            • Horários de maior atenção
            • Correlações importantes a monitorar
            • Indicadores para abortar operação
            
            📱 PLANOS ALTERNATIVOS
            • Plan B se setup falhar
            • Estratégia para mercado lateral
            • Ação em caso de gap adverso
            • Limites de perda do dia
            
            ✅ CHECKLIST DE EXECUÇÃO
            • [ ] Análise pre-market completa
            • [ ] Níveis marcados no gráfico
            • [ ] Stop loss configurado
            • [ ] Tamanho da posição definido
            • [ ] Plano de saída claro
            
            Formato: Markdown com valores específicos e horários exatos""",
            agent=agent,
            context=[research_task, technical_task],
            output_file=f"reports/daytrader_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

    def create_investment_recommendation_task(self, symbol: str, agent, all_previous_tasks: list) -> Task:
        """
        Cria tarefa de recomendação final de investimento.
        
        Args:
            symbol: Símbolo da ação
            agent: Agente responsável
            all_previous_tasks: Lista com todas as tarefas anteriores
            
        Returns:
            Task: Tarefa de recomendação final
        """
        return Task(
            description=f"""Sintetizar todas as análises realizadas sobre {symbol} e elaborar 
            recomendação final abrangente de investimento, considerando:

            1. SÍNTESE ANALÍTICA:
               • Consolidação dos insights de pesquisa
               • Integração da análise fundamentalista
               • Incorporação da análise técnica
               • Consideração das estratégias de day trade
               • Reconciliação de eventuais divergências

            2. CENÁRIOS DE INVESTIMENTO:
               • Cenário base: probabilidade e retorno esperado
               • Cenário otimista: drivers e potencial upside
               • Cenário pessimista: riscos e downside protection
               • Horizonte temporal para cada cenário

            3. RECOMENDAÇÃO ESTRATIFICADA:
               • Investidor conservador: estratégia e alocação
               • Investidor moderado: estratégia e alocação
               • Investidor agressivo: estratégia e alocação
               • Trader ativo: táticas de curto prazo

            4. TIMING DE INVESTIMENTO:
               • Momento ideal para entrada
               • Estratégia de acumulação gradual vs entrada única
               • Pontos de reavaliação da tese
               • Critérios para saída

            5. GESTÃO DE PORTFÓLIO:
               • Peso recomendado no portfólio
               • Correlações com outros ativos
               • Hedging e proteção de downside
               • Rebalanceamento periódico

            6. MONITORAMENTO E GATILHOS:
               • KPIs fundamentalistas para acompanhar
               • Níveis técnicos críticos
               • Eventos corporativos relevantes
               • Sinais de deterioração ou melhora

            7. CONSIDERAÇÕES ESPECIAIS:
               • Aspectos tributários relevantes
               • Liquidez e facilidade de execução
               • Questões de governança corporativa
               • Fatores ESG (se relevantes)

            Data da recomendação: {self.current_date}
            Validade da análise: 30 dias (sujeita a revisão)
            """,
            expected_output=f"""Recomendação de investimento completa para {symbol}:
            
            🏆 RECOMENDAÇÃO EXECUTIVA
            • Rating geral: [COMPRA FORTE/COMPRA/MANTENHA/VENDA/VENDA FORTE]
            • Preço-alvo 12 meses: R$ XX,XX
            • Potencial de retorno: XX%
            • Nível de risco: [BAIXO/MÉDIO/ALTO]
            • Convicção da recomendação: [ALTA/MÉDIA/BAIXA]
            
            📋 TESE DE INVESTIMENTO
            • Razões principais para a recomendação
            • Principais catalisadores de valor
            • Vantagens competitivas sustentáveis
            • Fatores de diferenciação vs peers
            
            🎯 CENÁRIOS DE INVESTIMENTO
            • OTIMISTA (30%): Retorno XX% - Drivers específicos
            • BASE (50%): Retorno XX% - Expectativas realistas
            • PESSIMISTA (20%): Retorno XX% - Principais riscos
            
            👥 RECOMENDAÇÕES POR PERFIL
            • CONSERVADOR: Estratégia, % portfólio, timing
            • MODERADO: Estratégia, % portfólio, timing
            • AGRESSIVO: Estratégia, % portfólio, timing
            • TRADER: Setups específicos e táticas
            
            ⏳ ESTRATÉGIA DE ENTRADA
            • Timing ideal: [IMEDIATA/AGUARDAR CORREÇÃO/GRADUAL]
            • Preço de entrada sugerido: R$ XX,XX
            • Estratégia de acumulação
            • Níveis de stop loss: R$ XX,XX
            
            📈 ALVOS E PRAZOS
            • Alvo 3 meses: R$ XX,XX (XX%)
            • Alvo 6 meses: R$ XX,XX (XX%)
            • Alvo 12 meses: R$ XX,XX (XX%)
            • Alvo 24 meses: R$ XX,XX (XX%)
            
            ⚠️ PRINCIPAIS RISCOS
            • Riscos fundamentalistas identificados
            • Riscos técnicos e de timing
            • Riscos macroeconômicos
            • Fatores que invalidariam a tese
            
            📊 MÉTRICAS DE ACOMPANHAMENTO
            • Indicadores fundamentalistas chave
            • Níveis técnicos críticos
            • Eventos corporativos a monitorar
            • Frequência de revisão recomendada
            
            🔄 GESTÃO DA POSIÇÃO
            • Peso máximo recomendado no portfólio
            • Estratégia de rebalanceamento
            • Critérios para aumento/redução da posição
            • Pontos de saída total
            
            💡 CONSIDERAÇÕES ESPECIAIS
            • Aspectos tributários relevantes
            • Questões de liquidez
            • Fatores de governança
            • Recomendações complementares
            
            Formato: Relatório executivo profissional em Markdown""",
            agent=agent,
            context=all_previous_tasks,
            output_file=f"reports/final_recommendation_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.md"
        )

    def create_all_tasks(self, symbol: str, agents: Dict[str, Any]) -> Dict[str, Task]:
        """
        Cria todas as tarefas para análise completa.
        
        Args:
            symbol: Símbolo da ação
            agents: Dicionário com todos os agentes
            
        Returns:
            Dict[str, Task]: Dicionário com todas as tarefas
        """
        # Cria as tarefas em ordem de dependência
        research_task = self.create_research_task(symbol, agents['research'])
        
        fundamental_task = self.create_fundamental_analysis_task(
            symbol, agents['fundamental'], research_task
        )
        
        technical_task = self.create_technical_analysis_task(
            symbol, agents['technical'], research_task
        )
        
        daytrader_task = self.create_daytrader_task(
            symbol, agents['daytrader'], research_task, technical_task
        )
        
        final_task = self.create_investment_recommendation_task(
            symbol, agents['consultant'], 
            [research_task, fundamental_task, technical_task, daytrader_task]
        )
        
        return {
            'research': research_task,
            'fundamental': fundamental_task,
            'technical': technical_task,
            'daytrader': daytrader_task,
            'final_recommendation': final_task
        }


# Função de conveniência
def create_market_tasks() -> MarketTasks:
    """
    Função de conveniência para criar uma instância de MarketTasks.
    
    Returns:
        MarketTasks: Instância configurada da classe
    """
    return MarketTasks()
