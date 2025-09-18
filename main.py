"""
Aplicação principal do sistema de análise de ações com CrewAI.
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
import argparse
from dotenv import load_dotenv

# Carrega variáveis de ambiente ANTES de importar outros módulos
load_dotenv()

# Adiciona o diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from crewai import Crew
from agents.market_agents import MarketAgents
from tasks.market_tasks import MarketTasks


class StockAnalysisApp:
    """Aplicação principal para análise de ações."""
    
    def __init__(self, llm_provider: Optional[str] = None):
        """
        Inicializa a aplicação.
        
        Args:
            llm_provider: Provedor de LLM a ser usado (openai, anthropic, deepseek, grok, ollama)
                         Se None, usa o provedor configurado em DEFAULT_LLM
        """
        # Verifica se as APIs estão configuradas
        self._check_api_keys()
        
        # Inicializa componentes
        self.market_agents = MarketAgents(llm_provider)
        self.market_tasks = MarketTasks()
        
        # Cria diretório de relatórios se não existir
        os.makedirs('reports', exist_ok=True)
        
        # Determina qual provedor está sendo usado para display
        from src.config.llm_config import llm_manager
        current_provider = llm_manager.default_provider.value if llm_provider is None else llm_provider
        current_config = llm_manager.get_config(llm_provider)
        
        print("🚀 Sistema de Análise de Ações CrewAI inicializado!")
        print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        print(f"🤖 Provedor LLM: {current_provider}")
        print(f"🧠 Modelo: {current_config.model}")
        print("-" * 60)

    def _check_api_keys(self):
        """Verifica se as chaves de API estão configuradas."""
        required_keys = {
            'ANTHROPIC_API_KEY': 'Anthropic (Claude)',
            'GOOGLE_API_KEY': 'Google Search (opcional)',
            'NEWS_API_KEY': 'News API (opcional)'
        }
        
        missing_keys = []
        for key, service in required_keys.items():
            if not os.getenv(key):
                if 'opcional' not in service:
                    missing_keys.append(f"{key} ({service})")
                else:
                    print(f"⚠️  {key} não configurada - {service}")
        
        if missing_keys:
            print("❌ Chaves de API obrigatórias não encontradas:")
            for key in missing_keys:
                print(f"   - {key}")
            print("\n💡 Configure as variáveis no arquivo .env")
            sys.exit(1)
        else:
            print("✅ Chaves de API configuradas corretamente")

    def analyze_stock(self, symbol: str, analysis_type: str = "complete") -> Dict[str, Any]:
        """
        Realiza análise completa de uma ação.
        
        Args:
            symbol: Símbolo da ação (ex: PETR4.SA)
            analysis_type: Tipo de análise (complete, quick, technical, fundamental)
            
        Returns:
            Dict com resultados da análise
        """
        print(f"\n📊 Iniciando análise de {symbol}")
        print(f"🔍 Tipo de análise: {analysis_type}")
        print("=" * 60)
        
        try:
            # Cria os agentes
            agents = self._create_agents_for_analysis(analysis_type)
            
            # Cria as tarefas
            tasks = self._create_tasks_for_analysis(symbol, agents, analysis_type)
            
            # Cria e executa o crew
            crew = Crew(
                agents=list(agents.values()),
                tasks=list(tasks.values()),
                verbose=True,
                memory=True,
                planning=True,
                max_execution_time=3600,  # 1 hora
                output_log_file=f"reports/execution_log_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M')}.log"
            )
            
            print(f"🎬 Executando análise com {len(agents)} agentes...")
            result = crew.kickoff()
            
            print(f"\n✅ Análise de {symbol} concluída com sucesso!")
            print(f"📁 Relatórios salvos na pasta 'reports/'")
            
            return {
                'symbol': symbol,
                'analysis_type': analysis_type,
                'result': result,
                'timestamp': datetime.now().isoformat(),
                'agents_used': list(agents.keys()),
                'tasks_completed': list(tasks.keys())
            }
            
        except Exception as e:
            print(f"❌ Erro durante análise de {symbol}: {str(e)}")
            return {
                'symbol': symbol,
                'analysis_type': analysis_type,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _create_agents_for_analysis(self, analysis_type: str) -> Dict[str, Any]:
        """Cria agentes baseado no tipo de análise."""
        agents = {}
        
        if analysis_type in ['complete', 'quick']:
            agents['research'] = self.market_agents.create_research_analyst()
            agents['fundamental'] = self.market_agents.create_fundamental_analyst()
            agents['technical'] = self.market_agents.create_technical_analyst()
            agents['consultant'] = self.market_agents.create_investment_consultant()
            
            if analysis_type == 'complete':
                agents['daytrader'] = self.market_agents.create_daytrader_consultant()
                
        elif analysis_type == 'technical':
            agents['research'] = self.market_agents.create_research_analyst()
            agents['technical'] = self.market_agents.create_technical_analyst()
            
        elif analysis_type == 'fundamental':
            agents['research'] = self.market_agents.create_research_analyst()
            agents['fundamental'] = self.market_agents.create_fundamental_analyst()
            
        return agents

    def _create_tasks_for_analysis(self, symbol: str, agents: Dict, analysis_type: str) -> Dict[str, Any]:
        """Cria tarefas baseado no tipo de análise."""
        tasks = {}
        
        # Tarefa de pesquisa sempre presente
        research_task = self.market_tasks.create_research_task(symbol, agents['research'])
        tasks['research'] = research_task
        
        if 'fundamental' in agents:
            tasks['fundamental'] = self.market_tasks.create_fundamental_analysis_task(
                symbol, agents['fundamental'], research_task
            )
        
        if 'technical' in agents:
            tasks['technical'] = self.market_tasks.create_technical_analysis_task(
                symbol, agents['technical'], research_task
            )
        
        if 'daytrader' in agents:
            tasks['daytrader'] = self.market_tasks.create_daytrader_task(
                symbol, agents['daytrader'], research_task, tasks.get('technical')
            )
        
        if 'consultant' in agents:
            previous_tasks = [task for key, task in tasks.items() if key != 'research']
            previous_tasks.insert(0, research_task)  # Adiciona research task no início
            
            tasks['final_recommendation'] = self.market_tasks.create_investment_recommendation_task(
                symbol, agents['consultant'], previous_tasks
            )
        
        return tasks

    def batch_analyze(self, symbols: list, analysis_type: str = "quick") -> Dict[str, Any]:
        """
        Realiza análise em lote de múltiplas ações.
        
        Args:
            symbols: Lista de símbolos para analisar
            analysis_type: Tipo de análise
            
        Returns:
            Dict com resultados de todas as análises
        """
        print(f"\n📊 Iniciando análise em lote de {len(symbols)} ações")
        print(f"🔍 Símbolos: {', '.join(symbols)}")
        print(f"🔍 Tipo: {analysis_type}")
        print("=" * 60)
        
        results = {}
        successful = 0
        failed = 0
        
        for i, symbol in enumerate(symbols, 1):
            print(f"\n[{i}/{len(symbols)}] Processando {symbol}...")
            
            try:
                result = self.analyze_stock(symbol, analysis_type)
                results[symbol] = result
                
                if 'error' in result:
                    failed += 1
                    print(f"❌ Falha na análise de {symbol}")
                else:
                    successful += 1
                    print(f"✅ Análise de {symbol} concluída")
                    
            except Exception as e:
                results[symbol] = {
                    'symbol': symbol,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                failed += 1
                print(f"❌ Erro crítico na análise de {symbol}: {str(e)}")
        
        print(f"\n📈 Análise em lote concluída!")
        print(f"✅ Sucessos: {successful}")
        print(f"❌ Falhas: {failed}")
        print(f"📁 Relatórios salvos na pasta 'reports/'")
        
        return {
            'batch_summary': {
                'total_symbols': len(symbols),
                'successful': successful,
                'failed': failed,
                'analysis_type': analysis_type,
                'timestamp': datetime.now().isoformat()
            },
            'results': results
        }

    def list_available_symbols(self) -> list:
        """Lista alguns símbolos populares da B3."""
        popular_symbols = [
            'PETR4.SA',  # Petrobras
            'VALE3.SA',  # Vale
            'ITUB4.SA',  # Itaú
            'BBDC4.SA',  # Bradesco
            'ABEV3.SA',  # Ambev
            'WEGE3.SA',  # WEG
            'MGLU3.SA',  # Magazine Luiza
            'RENT3.SA',  # Localiza
            'LREN3.SA',  # Lojas Renner
            'JBSS3.SA',  # JBS
            'SUZB3.SA',  # Suzano
            'VIVT3.SA',  # Telefônica
            'GGBR4.SA',  # Gerdau
            'USIM5.SA',  # Usiminas
            'CSNA3.SA',  # CSN
        ]
        
        return popular_symbols


def main():
    """Função principal da aplicação."""
    parser = argparse.ArgumentParser(description='Sistema de Análise de Ações CrewAI')
    parser.add_argument('symbol', nargs='?', help='Símbolo da ação (ex: PETR4.SA)')
    parser.add_argument('--type', choices=['complete', 'quick', 'technical', 'fundamental'], 
                       default='quick', help='Tipo de análise')
    parser.add_argument('--batch', nargs='*', help='Análise em lote (lista de símbolos)')
    parser.add_argument('--list-symbols', action='store_true', help='Lista símbolos populares')
    parser.add_argument('--model', default=None, help='Provedor LLM (openai, anthropic, deepseek, grok, ollama)')
    
    args = parser.parse_args()
    
    # Inicializa aplicação
    app = StockAnalysisApp(args.model) if args.model else StockAnalysisApp()
    
    if args.list_symbols:
        symbols = app.list_available_symbols()
        print("\n📋 Símbolos populares da B3:")
        for symbol in symbols:
            print(f"   • {symbol}")
        return
    
    if args.batch:
        # Análise em lote
        results = app.batch_analyze(args.batch, args.type)
        print(f"\n📊 Resultados salvos em arquivos individuais")
        
    elif args.symbol:
        # Análise individual
        result = app.analyze_stock(args.symbol, args.type)
        if 'error' not in result:
            print(f"\n📊 Análise de {args.symbol} concluída com sucesso!")
        else:
            print(f"\n❌ Erro na análise: {result['error']}")
    
    else:
        # Modo interativo
        print("\n🎯 Modo Interativo")
        print("Digite o símbolo da ação (ex: PETR4.SA) ou 'quit' para sair:")
        
        while True:
            try:
                symbol = input("\n> Símbolo: ").strip().upper()
                
                if symbol.lower() in ['quit', 'q', 'exit']:
                    print("👋 Até logo!")
                    break
                
                if not symbol:
                    continue
                
                # Adiciona .SA se não estiver presente
                if not symbol.endswith('.SA'):
                    symbol += '.SA'
                
                print(f"\n🔍 Analisando {symbol}...")
                result = app.analyze_stock(symbol, 'quick')
                
                if 'error' not in result:
                    print(f"✅ Análise concluída! Verifique os relatórios em 'reports/'")
                else:
                    print(f"❌ Erro: {result['error']}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Até logo!")
                break
            except Exception as e:
                print(f"❌ Erro inesperado: {str(e)}")


if __name__ == "__main__":
    main()
