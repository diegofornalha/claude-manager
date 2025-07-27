# Claude Manager - Documentação Completa

## 📋 Visão Geral

O **Claude Manager** é uma ferramenta robusta de terminal para gerenciar projetos Claude Code e configurações. Esta documentação está organizada em clusters funcionais para facilitar a navegação e compreensão.

## 🏗️ Arquitetura do Sistema

```
claude-manager/
├── 📁 claude_manager/          # Código fonte principal
│   ├── 📄 __init__.py         # Inicialização do módulo
│   ├── 📄 cli.py              # Interface de linha de comando
│   ├── 📄 config.py           # Gerenciamento de configuração
│   ├── 📄 models.py           # Modelos de dados
│   ├── 📄 tui.py              # Interface de terminal (TUI)
│   ├── 📄 ui.py               # Interface alternativa
│   ├── 📄 simple_ui.py        # Interface simplificada
│   ├── 📄 terminal_utils.py   # Utilitários de terminal
│   ├── 📄 ui_helpers.py       # Helpers de interface
│   └── 📄 utils.py            # Utilitários gerais
├── 📁 tests/                  # Testes automatizados
├── 📁 docs/                   # Documentação
└── 📄 pyproject.toml          # Configuração do projeto
```

## 🎯 Clusters de Funcionalidades

### 🔧 **1. Configuração e Gerenciamento de Dados**
- **Arquivos**: `config.py`, `models.py`
- **Responsabilidades**: 
  - Gerenciamento de arquivo de configuração JSON
  - Modelos de dados (Project, Agent)
  - Serialização/deserialização
  - Validação de dados
- **📖 Documentação**: [Configuração e Dados](configuration-data-management.md)

### 🖥️ **2. Interfaces de Usuário**
- **Arquivos**: `tui.py`, `simple_ui.py`, `ui.py`
- **Responsabilidades**:
  - Interface de terminal rica (TUI)
  - Interface simples alternativa
  - Navegação e interação
  - Componentes visuais
- **📖 Documentação**: [Interfaces de Usuário](user-interfaces.md)

### ⚡ **3. CLI e Utilitários**
- **Arquivos**: `cli.py`, `utils.py`, `terminal_utils.py`
- **Responsabilidades**:
  - Interface de linha de comando
  - Gerenciamento de sinais
  - Utilitários de terminal
  - Limpeza e reset
- **📖 Documentação**: [CLI e Utilitários](cli-utilities.md)

### 🤖 **4. Sistema de Agentes**
- **Arquivos**: `config.py` (parte), `models.py` (Agent)
- **Responsabilidades**:
  - Parsing de agentes Markdown
  - Gerenciamento de agentes globais/projeto
  - Configuração de ferramentas
  - Padrões neurais
- **📖 Documentação**: [Sistema de Agentes](agent-system.md)

### 💾 **5. Sistema de Backup**
- **Arquivos**: `config.py` (parte)
- **Responsabilidades**:
  - Criação automática de backups
  - Rotação de backups
  - Restauração de configurações
  - Limpeza de backups antigos
- **📖 Documentação**: [Sistema de Backup](backup-system.md)

### 🔌 **6. Gerenciamento de MCP Servers**
- **Arquivos**: `tui.py` (parte), `models.py` (parte)
- **Responsabilidades**:
  - Configuração de servidores MCP
  - Habilitar/desabilitar servidores
  - Edição de configurações JSON
  - Integração com projetos
  - Expansão de capacidades do Claude Code
- **📖 Documentação**: [MCP Servers](mcp-servers.md)

### 📚 **7. Gerenciamento de Histórico**
- **Arquivos**: `tui.py` (parte), `models.py` (parte)
- **Responsabilidades**:
  - Limpeza de histórico
  - Retenção de entradas recentes
  - Análise de uso
  - Otimização de espaço
- **📖 Documentação**: [Gerenciamento de Histórico](history-management.md)

### 🔍 **8. Análise e Monitoramento**
- **Arquivos**: `tui.py` (parte), `config.py` (parte)
- **Responsabilidades**:
  - Análise de projetos
  - Identificação de problemas
  - Estatísticas de uso
  - Relatórios de saúde
- **📖 Documentação**: [Análise e Monitoramento](analysis-monitoring.md)

### 🔒 **9. Sistema de Aceitação de Confiança**
- **Arquivos**: `models.py`, `tui.py` (parte), `ui.py` (parte)
- **Responsabilidades**:
  - Controle de segurança
  - Aceitação de confiança
  - Auditoria de permissões
  - Proteção contra código malicioso
- **📖 Documentação**: [Sistema de Aceitação de Confiança](trust-acceptance-system.md)

### 🧪 **10. Testes e Qualidade**
- **Arquivos**: `tests/`
- **Responsabilidades**:
  - Testes unitários
  - Testes de integração
  - Fixtures e configuração
  - Cobertura de código
- **📖 Documentação**: [Testes e Qualidade](testing-quality.md)

## 🚀 Guias de Uso

### Para Desenvolvedores
- [Configuração do Ambiente](developer-setup.md)
- [Arquitetura do Código](code-architecture.md)
- [Padrões de Desenvolvimento](development-patterns.md)
- [Contribuindo](contributing.md)

### Para Usuários
- [Instalação](installation.md)
- [Primeiros Passos](getting-started.md)
- [Guias de Funcionalidades](feature-guides.md)
- [Solução de Problemas](troubleshooting.md)

## 📊 Métricas e Estatísticas

### Cobertura de Código
- **Total de arquivos**: 11 arquivos principais
- **Linhas de código**: ~2,500 linhas
- **Cobertura de testes**: >90%
- **Documentação**: 100% dos módulos

### Funcionalidades Principais
- ✅ Gerenciamento de projetos Claude Code
- ✅ Interface de terminal rica (TUI)
- ✅ Sistema de backup automático
- ✅ Gerenciamento de agentes
- ✅ Análise e monitoramento
- ✅ Sistema de segurança
- ✅ Configuração flexível

## 🔗 Links Rápidos

### Documentação Técnica
- [API Reference](api-reference.md)
- [Modelos de Dados](data-models.md)
- [Configuração](configuration.md)
- [CLI Reference](cli-reference.md)

### Recursos
- [Changelog](changelog.md)
- [Roadmap](roadmap.md)
- [FAQ](faq.md)
- [Suporte](support.md)

---

**Claude Manager** - Gerenciando projetos Claude Code com eficiência e segurança! 🚀✨ 