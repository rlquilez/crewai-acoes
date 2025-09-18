# Guia de Contribuição

Obrigado por considerar contribuir com o CrewAI Stock Analysis! 🚀

## 📋 Índice

- [Como Contribuir](#como-contribuir)
- [Configuração de Desenvolvimento](#configuração-de-desenvolvimento)
- [Padrões de Código](#padrões-de-código)
- [Testes](#testes)
- [Submissão de Pull Requests](#submissão-de-pull-requests)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Funcionalidades](#sugerindo-funcionalidades)

## Como Contribuir

### 🔧 Tipos de Contribuições

Valorizamos vários tipos de contribuições:

- **🐛 Correção de Bugs**: Identificação e correção de problemas
- **✨ Novas Funcionalidades**: Implementação de recursos
- **📚 Documentação**: Melhoria da documentação
- **🔧 Refatoração**: Melhorias no código existente
- **🧪 Testes**: Adição ou melhoria de testes
- **🎨 UI/UX**: Melhorias na interface
- **⚡ Performance**: Otimizações de performance

### 🚀 Configuração de Desenvolvimento

1. **Fork o repositório**
   ```bash
   # No GitHub, clique em "Fork"
   git clone https://github.com/SEU_USUARIO/crewai-acoes.git
   cd crewai-acoes
   ```

2. **Configure o ambiente**
   ```bash
   # Crie ambiente virtual
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou venv\Scripts\activate  # Windows
   
   # Instale dependências de desenvolvimento
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. **Configure variáveis de ambiente**
   ```bash
   cp .env.example .env
   # Configure suas APIs no arquivo .env
   ```

4. **Configure pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 🎯 Padrões de Código

### Estilo de Código

- **Python**: Seguimos PEP 8
- **Formatação**: Black (configurado no pre-commit)
- **Linting**: Flake8 + pylint
- **Type Hints**: Obrigatório para funções públicas
- **Docstrings**: Google Style

### Exemplo de Função

```python
def analyze_stock(symbol: str, analysis_type: str = "quick") -> Dict[str, Any]:
    """
    Analisa uma ação específica.
    
    Args:
        symbol: Símbolo da ação (ex: PETR4.SA)
        analysis_type: Tipo de análise a realizar
        
    Returns:
        Dict contendo os resultados da análise
        
    Raises:
        ValueError: Se o símbolo for inválido
        APIError: Se houver erro nas APIs externas
    """
    # Implementação aqui
    pass
```

### Estrutura de Commits

Usamos [Conventional Commits](https://www.conventionalcommits.org/):

```
<tipo>(<escopo>): <descrição>

<corpo opcional>

<rodapé opcional>
```

**Tipos:**
- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Mudanças na documentação
- `style`: Formatação, sem mudança de lógica
- `refactor`: Refatoração de código
- `test`: Adição ou correção de testes
- `chore`: Tarefas de manutenção

**Exemplos:**
```bash
feat(agents): adiciona agente de análise de opções
fix(yfinance): corrige erro de timeout na API
docs(readme): atualiza instruções de instalação
test(calculator): adiciona testes para RSI
```

## 🧪 Testes

### Executando Testes

```bash
# Todos os testes
python -m pytest

# Com coverage
python -m pytest --cov=src --cov-report=html

# Testes específicos
python -m pytest tests/test_agents.py

# Testes com markers
python -m pytest -m "not slow"
```

### Escrevendo Testes

```python
import pytest
from src.tools.calculator_tools import CalculatorTools

class TestCalculatorTools:
    """Testes para CalculatorTools."""
    
    def test_calculate_basic_operation(self):
        """Testa operações matemáticas básicas."""
        result = CalculatorTools.calculate("2 + 2")
        assert "4" in result
    
    @pytest.mark.parametrize("expression,expected", [
        ("10 / 2", "5"),
        ("3 * 4", "12"),
        ("10 - 3", "7"),
    ])
    def test_calculate_parametrized(self, expression, expected):
        """Testa múltiplas operações."""
        result = CalculatorTools.calculate(expression)
        assert expected in result
    
    def test_calculate_division_by_zero(self):
        """Testa divisão por zero."""
        result = CalculatorTools.calculate("1 / 0")
        assert "Erro" in result
```

### Fixtures Úteis

```python
@pytest.fixture
def sample_stock_data():
    """Dados de exemplo para testes."""
    return {
        'symbol': 'PETR4.SA',
        'prices': [25.0, 26.0, 24.5, 27.0, 28.0],
        'volumes': [1000000, 1200000, 800000, 1500000, 1100000]
    }

@pytest.fixture
def mock_yfinance(mocker):
    """Mock do Yahoo Finance."""
    mock = mocker.patch('yfinance.Ticker')
    mock.return_value.info = {'currentPrice': 25.50}
    return mock
```

## 📤 Submissão de Pull Requests

### Processo

1. **Crie uma branch**
   ```bash
   git checkout -b feature/nova-funcionalidade
   ```

2. **Desenvolva e teste**
   ```bash
   # Faça suas mudanças
   git add .
   git commit -m "feat: adiciona nova funcionalidade"
   ```

3. **Sincronize com main**
   ```bash
   git fetch upstream
   git rebase upstream/main
   ```

4. **Push e PR**
   ```bash
   git push origin feature/nova-funcionalidade
   # Crie PR no GitHub
   ```

### Checklist do PR

- [ ] Código segue os padrões estabelecidos
- [ ] Testes passam (`pytest`)
- [ ] Documentação atualizada
- [ ] Changelog atualizado (se necessário)
- [ ] Commit messages seguem convenção
- [ ] PR tem descrição clara
- [ ] Screenshots (se UI changes)

### Template de PR

```markdown
## Descrição
Breve descrição das mudanças.

## Tipo de Mudança
- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Testes
- [ ] Testes existentes passam
- [ ] Novos testes adicionados
- [ ] Testado manualmente

## Screenshots
(Se aplicável)

## Checklist
- [ ] Code review próprio realizado
- [ ] Documentação atualizada
- [ ] Changelog atualizado
```

## 🐛 Reportando Bugs

### Template de Bug Report

```markdown
**Descrição do Bug**
Descrição clara e concisa do problema.

**Reproduzir**
Passos para reproduzir:
1. Execute comando '...'
2. Com parâmetros '...'
3. Veja o erro

**Comportamento Esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável, adicione screenshots.

**Ambiente:**
- OS: [Windows/Mac/Linux]
- Python: [3.11.0]
- CrewAI: [0.56.0]
- Docker: [Sim/Não]

**Logs**
```
Cole logs relevantes aqui
```

**Contexto Adicional**
Qualquer outra informação relevante.
```

### Labels de Issues

- `bug`: Problema confirmado
- `enhancement`: Nova funcionalidade
- `documentation`: Melhoria na documentação
- `good first issue`: Bom para iniciantes
- `help wanted`: Precisa de ajuda
- `priority:high`: Alta prioridade
- `priority:low`: Baixa prioridade

## ✨ Sugerindo Funcionalidades

### Template de Feature Request

```markdown
**Problema/Necessidade**
Descreva o problema que esta funcionalidade resolveria.

**Solução Proposta**
Descrição clara da solução desejada.

**Alternativas Consideradas**
Outras soluções que você considerou.

**Contexto Adicional**
Screenshots, mockups, links, etc.

**Complexidade Estimada**
- [ ] Baixa (1-2 dias)
- [ ] Média (1 semana)
- [ ] Alta (2+ semanas)
```

## 📚 Recursos Adicionais

### Documentação Técnica

- [CrewAI Documentation](https://docs.crewai.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Yahoo Finance API](https://pypi.org/project/yfinance/)

### Comunidade

- **Discord**: [CrewAI Brasil](https://discord.gg/crewai-brasil)
- **Discussions**: [GitHub Discussions](https://github.com/rlquilez/crewai-acoes/discussions)
- **Email**: suporte@crewai-acoes.com

### Desenvolvimento

- **Project Board**: [GitHub Projects](https://github.com/rlquilez/crewai-acoes/projects)
- **Wiki**: [GitHub Wiki](https://github.com/rlquilez/crewai-acoes/wiki)
- **Releases**: [GitHub Releases](https://github.com/rlquilez/crewai-acoes/releases)

## 🏆 Reconhecimento

Contribuidores são reconhecidos em:

- **README.md**: Lista de contribuidores
- **CHANGELOG.md**: Créditos nas releases
- **GitHub**: Contributor insights
- **Discord**: Role especial para contributors

## 📄 Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a MIT License.

---

**Obrigado por contribuir! 🙏**

Sua ajuda torna este projeto melhor para toda a comunidade.
