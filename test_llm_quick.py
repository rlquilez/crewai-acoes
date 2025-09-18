#!/usr/bin/env python3
"""
Teste rápido para verificar se o problema do LLM foi resolvido
"""

import os
import sys
from pathlib import Path

# Carrega variáveis de ambiente
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ dotenv carregado")
except ImportError:
    print("⚠️ python-dotenv não disponível")

# Adiciona src ao path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def test_llm_configuration():
    """Testa se a configuração de LLM está correta"""
    print("=== TESTE DE CONFIGURAÇÃO LLM ===")
    print()
    
    # Testa importação dos agentes
    try:
        from agents.market_agents import MarketAgents
        
        print("✓ Importação dos agentes: OK")
        
        # Cria instância dos agentes
        market_agents = MarketAgents()
        print(f"✓ Agentes criados com LLM: {type(market_agents.llm).__name__}")
        
        # Verifica o modelo do LLM
        if hasattr(market_agents.llm, 'model'):
            print(f"✓ Modelo configurado: {market_agents.llm.model}")
        elif hasattr(market_agents.llm, 'model_name'):
            print(f"✓ Modelo configurado: {market_agents.llm.model_name}")
        
        # Cria um agente de teste
        test_agent = market_agents.create_research_analyst()
        print(f"✓ Agente criado: {test_agent.role}")
        print(f"✓ LLM do agente: {type(test_agent.llm).__name__}")
        
        if hasattr(test_agent.llm, 'model'):
            print(f"✓ Modelo do agente: {test_agent.llm.model}")
        elif hasattr(test_agent.llm, 'model_name'):
            print(f"✓ Modelo do agente: {test_agent.llm.model_name}")
            
        return True
        
    except Exception as e:
        print(f"✗ Erro ao testar agentes: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_crew_creation():
    """Testa criação de crew com Deepseek"""
    print("\n=== TESTE DE CRIAÇÃO CREW ===")
    print()
    
    try:
        from agents.market_agents import MarketAgents
        from tasks.market_tasks import MarketTasks
        from crewai import Crew
        from config import get_llm
        
        # Cria componentes
        market_agents = MarketAgents()
        market_tasks = MarketTasks()
        crew_llm = get_llm()
        
        print(f"✓ LLM do Crew: {type(crew_llm).__name__}")
        
        # Cria agente de teste
        agent = market_agents.create_research_analyst()
        task = market_tasks.create_research_task("PETR4.SA", agent)
        
        # Cria crew mínimo
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False,
            planning=False,
            manager_llm=crew_llm
        )
        
        print("✓ Crew criado com sucesso")
        print(f"✓ Manager LLM: {type(crew.manager_llm).__name__ if hasattr(crew, 'manager_llm') else 'Não definido'}")
        
        return True
        
    except Exception as e:
        print(f"✗ Erro ao criar crew: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Executa todos os testes"""
    print("🧪 TESTE RÁPIDO DE LLM")
    print("=" * 40)
    
    # Verifica variáveis de ambiente
    print(f"DEFAULT_LLM: {os.getenv('DEFAULT_LLM', 'NÃO DEFINIDO')}")
    print(f"DEEPSEEK_MODEL: {os.getenv('DEEPSEEK_MODEL', 'NÃO DEFINIDO')}")
    print()
    
    # Executa testes
    llm_ok = test_llm_configuration()
    crew_ok = test_crew_creation()
    
    print()
    print("=" * 40)
    print("📊 RESULTADO:")
    print(f"LLM Config: {'✓' if llm_ok else '✗'}")
    print(f"Crew Config: {'✓' if crew_ok else '✗'}")
    
    if llm_ok and crew_ok:
        print("\n🎉 CONFIGURAÇÃO OK!")
        print("Pode executar: python main.py PETR4.SA")
    else:
        print("\n❌ PROBLEMAS ENCONTRADOS")
        print("Verifique os erros acima")

if __name__ == "__main__":
    main()