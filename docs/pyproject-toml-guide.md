# Guia do pyproject.toml - Claude Manager

O `pyproject.toml` é o arquivo de configuração moderno para projetos Python, substituindo múltiplos arquivos de configuração antigos como `setup.py`, `setup.cfg`, `requirements.txt`, e configurações específicas de ferramentas.

## Índice
- [Visão Geral](#visão-geral)
- [Estrutura do Arquivo](#estrutura-do-arquivo)
- [Seções Detalhadas](#seções-detalhadas)
- [Como Usar](#como-usar)
- [Comparação com requirements.txt](#comparação-com-requirementstxt)

## Visão Geral

O `pyproject.toml` segue as especificações:
- **PEP 518**: Define o formato básico e a seção `[build-system]`
- **PEP 621**: Define metadados do projeto na seção `[project]`
- **PEP 517**: Define a interface de build

## Estrutura do Arquivo

### 1. Build System (`[build-system]`)
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```
- **requires**: Ferramentas necessárias para construir o pacote
- **build-backend**: Sistema de build usado (neste caso, Hatchling)

### 2. Metadados do Projeto (`[project]`)
```toml
[project]
name = "claude-manager"
version = "1.0.0"
description = "A robust terminal UI for managing Claude Code projects..."
```

#### Campos Principais:
- **name**: Nome do pacote no PyPI
- **version**: Versão seguindo semantic versioning
- **description**: Descrição curta do projeto
- **readme**: Arquivo README do projeto
- **license**: Tipo de licença (MIT neste caso)
- **authors/maintainers**: Responsáveis pelo projeto

#### Classificadores
```toml
classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Programming Language :: Python :: 3.8",
    ...
]
```
Metadados padronizados que ajudam usuários a encontrar e entender o projeto no PyPI.

### 3. Dependências (`dependencies`)
```toml
dependencies = [
    "rich>=13.7.0",        # Formatação rica no terminal
    "textual>=0.47.0",     # Framework para TUI
    "click>=8.1.0",        # Interface de linha de comando
    "typing-extensions>=4.0.0; python_version < '3.11'",  # Compatibilidade
]
```

### 4. Dependências Opcionais (`[project.optional-dependencies]`)
```toml
[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",       # Framework de testes
    "pytest-cov>=4.1.0",   # Cobertura de código
    "mypy>=1.5.0",         # Verificação de tipos
    "ruff>=0.1.0",         # Linter rápido
    "black>=23.0.0",       # Formatador de código
    ...
]
```

Instalar com: `pip install -e ".[dev]"`

### 5. Scripts/Entry Points (`[project.scripts]`)
```toml
[project.scripts]
claude-manager = "claude_manager.cli:main"
```
Define o comando `claude-manager` que executa a função `main` em `claude_manager.cli`.

### 6. Configuração do Hatch (`[tool.hatch.*]`)
```toml
[tool.hatch.build.targets.wheel]
packages = ["src/claude_manager"]
```
Especifica como construir o pacote wheel.

### 7. Configuração do Pytest (`[tool.pytest.ini_options]`)
```toml
[tool.pytest.ini_options]
addopts = [
    "-ra",                          # Mostra resumo de todos os testes
    "--strict-markers",             # Força declaração de markers
    "--cov=claude_manager",         # Cobertura de código
    "--cov-branch",                 # Inclui cobertura de branches
]
testpaths = ["tests"]
pythonpath = ["src"]
```

### 8. Configuração do Coverage (`[tool.coverage.*]`)
```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    ...
]
```
Define linhas ignoradas na análise de cobertura.

### 9. Configuração do MyPy (`[tool.mypy]`)
```toml
[tool.mypy]
python_version = "3.8"
strict = true              # Modo estrito de verificação
warn_return_any = true     # Avisa sobre retornos Any
```

### 10. Configuração do Ruff (`[tool.ruff]`)
```toml
[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "F",    # pyflakes
    "I",    # isort
    ...
]
```
Ruff é um linter Python extremamente rápido que substitui múltiplas ferramentas.

#### Regras por Arquivo
```toml
[tool.ruff.lint.per-file-ignores]
"tests/*" = ["S101", "PLR2004", "ANN"]  # Ignora certas regras em testes
```

### 11. Configuração do Black (`[tool.black]`)
```toml
[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312"]
```
Black é um formatador de código opinativo.

### 12. Configuração do isort (`[tool.isort]`)
```toml
[tool.isort]
profile = "black"          # Compatível com Black
line_length = 100
```
Organiza imports automaticamente.

## Como Usar

### Instalação Básica
```bash
# Instala o projeto em modo editável
pip install -e .
```

### Instalação com Desenvolvimento
```bash
# Instala com todas as ferramentas de desenvolvimento
pip install -e ".[dev]"
```

### Instalação com Documentação
```bash
# Instala com ferramentas de documentação
pip install -e ".[docs]"
```

### Executar Testes
```bash
pytest
```

### Executar Linters
```bash
ruff check .
mypy src/
black --check .
```

### Formatar Código
```bash
black .
isort .
```

## Comparação com requirements.txt

### requirements.txt (Antigo)
```txt
rich>=13.7.0
textual>=0.47.0
click>=8.1.0
```

**Limitações:**
- Apenas lista dependências
- Sem metadados do projeto
- Sem configuração de ferramentas
- Múltiplos arquivos necessários (setup.py, setup.cfg, etc.)

### pyproject.toml (Moderno)
**Vantagens:**
- ✅ Arquivo único para toda configuração
- ✅ Metadados estruturados
- ✅ Dependências opcionais organizadas
- ✅ Configuração de ferramentas integrada
- ✅ Padrão oficial (PEPs)
- ✅ Melhor para CI/CD
- ✅ Suporte nativo no pip moderno

## Conclusão

O `pyproject.toml` centraliza toda a configuração do projeto Python, tornando-o mais mantenível e seguindo os padrões modernos da comunidade. Para o Claude Manager, ele gerencia:

1. **Dependências de produção**: rich, textual, click
2. **Ferramentas de desenvolvimento**: pytest, mypy, ruff, black
3. **Configurações de qualidade**: linting, formatação, testes
4. **Metadados do projeto**: versão, autores, licença
5. **Build e distribuição**: como criar pacotes wheel/sdist

Isso simplifica o desenvolvimento e garante consistência em toda a equipe.