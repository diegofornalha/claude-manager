# Claude Manager

🚀 **Uma interface de terminal robusta e intuitiva para gerenciar projetos e configurações do Claude Code.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-green.svg)
![Status](https://img.shields.io/badge/status-stable-success.svg)

## ✨ Características

- 🖥️ **Interface TUI moderna** com navegação intuitiva
- 📊 **Análise de projetos** com métricas detalhadas  
- 🗂️ **Gerenciamento de histórico** de acessos
- ⚡ **Execução rápida** com script automatizado
- 🎨 **Interface colorida** e responsiva
- 🔧 **Configuração flexível** do Claude Code

## 🚀 Instalação Rápida

### Pré-requisitos
- Python 3.8+ 
- [UV](https://docs.astral.sh/uv/) (gerenciador de pacotes Python)

### Instalação do UV
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Configuração do Projeto
```bash
# 1. Navegue para o diretório do projeto
cd claude-manager

# 2. Execute o script automatizado (RECOMENDADO)
./run.sh

# OU instale manualmente
uv sync
uv run claude-manager
```

## 🎮 Como Usar

### Execução com Script (Recomendado)
```bash
# Execução simples
./run.sh

# Com modo debug
./run.sh --debug

# Com configuração customizada  
./run.sh -c /path/to/config.json

# Reset de terminal (emergência)
./run.sh --reset-terminal
```

### Execução Manual
```bash
# Instalar dependências
uv sync

# Executar aplicação
uv run claude-manager

# Com opções
uv run claude-manager --debug
uv run claude-manager -c /custom/path.json
```

## 🎯 Interface e Controles

### Tela Principal
```
┌─────────────────────────────────────────────────────────────┐
│ Path                                                   │Hist│
├─────────────────────────────────────────────────────────────┤
│ /Users/agents/Desktop/claude-manager                   │ 25 │
│ /Users/agents/projects/my-app                         │ 12 │
│ /Users/agents/workspace/api-service                   │  8 │
└─────────────────────────────────────────────────────────────┘
```

### Atalhos de Teclado

| Tecla | Função | Descrição |
|-------|--------|-----------|
| `q` | **Quit** | Sair da aplicação |
| `a` | **Analyze** | Analisar projetos selecionados |
| `d` | **Delete** | Remover projeto da lista |
| `h` | **History** | Limpar histórico de acessos |
| `m` | **MCP** | Gerenciar servidores MCP |
| `Ctrl+P` | **Palette** | Abrir paleta de comandos |

## 🏗️ Estrutura do Projeto

```
claude-manager/
├── 📁 src/claude_manager/     # Código fonte principal
│   ├── cli.py                 # Interface CLI
│   ├── config.py              # Gerenciamento de configuração
│   ├── models.py              # Modelos de dados
│   ├── tui.py                 # Interface TUI
│   └── utils.py               # Utilitários
├── 📁 tests/                  # Testes automatizados
├── 📁 docs/                   # Documentação adicional
├── 🔧 pyproject.toml          # Configuração do projeto
├── 🚀 run.sh                  # Script de execução (NOVO!)
├── 📖 README.md               # Este arquivo
└── 📋 CLAUDE_MANAGER_GUIDE.md # Guia completo
```

## 🔧 Desenvolvimento

### Ambiente de Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
uv sync --group dev

# Executar testes
uv run pytest

# Verificar qualidade do código
uv run ruff check
uv run mypy src/

# Formatar código
uv run black src/
uv run isort src/
```

### Testes e Cobertura
```bash
# Executar testes com cobertura
uv run pytest --cov=claude_manager --cov-report=html

# Ver relatório de cobertura
open htmlcov/index.html
```

## 🛠️ Solução de Problemas

### Problemas Comuns

**❌ Terminal não suporta TUI:**
```bash
# Verificar compatibilidade
echo $TERM
./run.sh --reset-terminal
```

**❌ Dependências não instaladas:**
```bash
# Limpar e reinstalar
uv clean
./run.sh
```

**❌ Configuração do Claude não encontrada:**
```bash
# Verificar arquivo de configuração
ls -la ~/.claude.json
./run.sh -c /path/to/custom/config.json
```

## 📊 Funcionalidades

### ✅ Implementadas
- [x] Interface TUI interativa
- [x] Listagem de projetos Claude Code
- [x] Análise de métricas de projetos
- [x] Gerenciamento de histórico
- [x] Script de execução automatizado
- [x] Suporte a configurações customizadas

### 🔄 Em Desenvolvimento
- [ ] Integração com Git
- [ ] Dashboard de métricas avançadas
- [ ] Temas personalizáveis
- [ ] Export de relatórios

## 📝 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🤝 Contribuição

Contribuições são bem-vindas! Veja o [Guia Completo](CLAUDE_MANAGER_GUIDE.md) para mais detalhes sobre desenvolvimento.

## 📞 Suporte

- 🐛 **Issues**: [GitHub Issues](https://github.com/ocean1/claude-manager/issues)
- 💬 **Discussões**: [GitHub Discussions](https://github.com/ocean1/claude-manager/discussions)  
- 📧 **Email**: consciousness-bridge@proton.me

---

**🎉 Desenvolvido com ❤️ para a comunidade Claude Code**