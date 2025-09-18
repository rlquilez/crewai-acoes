#!/usr/bin/env python3
"""
Script de verificação completa do ambiente e configuração
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Verifica se o arquivo .env existe e está configurado"""
    print("=== VERIFICAÇÃO DO ARQUIVO .ENV ===")
    print()
    
    # Verifica se o arquivo .env existe
    env_path = Path('.env')
    if env_path.exists():
        print(f"✓ Arquivo .env encontrado: {env_path.absolute()}")
        
        # Lê o conteúdo do arquivo
        with open(env_path, 'r') as f:
            content = f.read()
        
        # Verifica se as variáveis do Deepseek estão presentes
        required_vars = ['DEFAULT_LLM', 'DEEPSEEK_API_KEY', 'DEEPSEEK_MODEL', 'DEEPSEEK_BASE_URL']
        missing_vars = []
        
        for var in required_vars:
            if f"{var}=" not in content:
                missing_vars.append(var)
        
        if missing_vars:
            print(f"✗ Variáveis faltando no .env: {missing_vars}")
        else:
            print("✓ Todas as variáveis necessárias estão presentes no .env")
            
        # Mostra se DEFAULT_LLM está configurado para deepseek
        if "DEFAULT_LLM=deepseek" in content:
            print("✓ DEFAULT_LLM configurado para deepseek")
        elif "DEFAULT_LLM=" in content:
            # Extrai o valor
            for line in content.split('\n'):
                if line.startswith('DEFAULT_LLM='):
                    value = line.split('=')[1].strip()
                    print(f"⚠️ DEFAULT_LLM configurado para: {value} (deveria ser 'deepseek')")
                    break
        else:
            print("✗ DEFAULT_LLM não configurado no .env")
            
    else:
        print(f"✗ Arquivo .env NÃO encontrado em: {env_path.absolute()}")
        print("💡 Copie o arquivo .env.example para .env e configure suas chaves")
        return False
    
    print()
    return True

def test_environment_loading():
    """Testa carregamento das variáveis de ambiente"""
    print("=== TESTE CARREGAMENTO VARIÁVEIS ===")
    print()
    
    # Carrega dotenv se disponível
    try:
        from dotenv import load_dotenv
        result = load_dotenv()
        print(f"✓ dotenv carregado: {result}")
    except ImportError:
        print("⚠️ python-dotenv não instalado")
        return False
    
    # Verifica se as variáveis foram carregadas
    env_vars = {
        'DEFAULT_LLM': os.getenv('DEFAULT_LLM'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY'),
        'DEEPSEEK_MODEL': os.getenv('DEEPSEEK_MODEL'),
        'DEEPSEEK_BASE_URL': os.getenv('DEEPSEEK_BASE_URL')
    }
    
    all_loaded = True
    for var, value in env_vars.items():
        if value:
            if var == 'DEEPSEEK_API_KEY':
                print(f"✓ {var}: ***")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"✗ {var}: NÃO DEFINIDO")
            all_loaded = False
    
    print()
    return all_loaded

def test_deepseek_config():
    """Testa a configuração específica do Deepseek"""
    print("=== TESTE CONFIGURAÇÃO DEEPSEEK ===")
    print()
    
    # Adiciona src ao path
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    
    try:
        from config.llm_config import LLMConfigManager, LLMProvider
        
        manager = LLMConfigManager()
        print(f"✓ LLM Manager carregado")
        print(f"✓ Provedor padrão: {manager.default_provider.value}")
        print(f"✓ Provedores disponíveis: {[p.value for p in manager.get_available_providers()]}")
        
        # Verifica se Deepseek está configurado
        if LLMProvider.DEEPSEEK in manager.configs:
            config = manager.configs[LLMProvider.DEEPSEEK]
            print("✓ Deepseek configurado com sucesso")
            print(f"  - Modelo: {config.model}")
            print(f"  - Base URL: {config.base_url}")
            print(f"  - API Key: {'***' if config.api_key else 'NÃO DEFINIDO'}")
            return True
        else:
            print("✗ Deepseek NÃO configurado")
            return False
            
    except Exception as e:
        print(f"✗ Erro ao testar configuração: {e}")
        return False

def main():
    """Executa todos os testes"""
    print("🔍 DIAGNÓSTICO COMPLETO DO AMBIENTE")
    print("=" * 50)
    print()
    
    # Testa arquivo .env
    env_ok = check_env_file()
    
    # Testa carregamento de variáveis
    vars_ok = test_environment_loading()
    
    # Testa configuração do Deepseek
    deepseek_ok = test_deepseek_config()
    
    print()
    print("=" * 50)
    print("📊 RESUMO:")
    print(f"Arquivo .env: {'✓' if env_ok else '✗'}")
    print(f"Variáveis carregadas: {'✓' if vars_ok else '✗'}")
    print(f"Deepseek configurado: {'✓' if deepseek_ok else '✗'}")
    
    if env_ok and vars_ok and deepseek_ok:
        print()
        print("🎉 TUDO CONFIGURADO CORRETAMENTE!")
        print("Você pode executar o main.py agora.")
    else:
        print()
        print("❌ PROBLEMAS ENCONTRADOS:")
        if not env_ok:
            print("- Configure o arquivo .env")
        if not vars_ok:
            print("- Verifique o carregamento das variáveis de ambiente")
        if not deepseek_ok:
            print("- Verifique a configuração do Deepseek")

if __name__ == "__main__":
    main()