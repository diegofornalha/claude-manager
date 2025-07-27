# Claude Manager - Guia Completo

## 📋 Visão Geral

O **Claude Manager** é uma interface de terminal robusta e intuitiva para gerenciar projetos e configurações do Claude Code. Desenvolvido em Python usando as bibliotecas Textual e Rich, oferece uma experiência de usuário moderna e eficiente diretamente no terminal.

## 🚀 Características Principais

### Interface TUI (Terminal User Interface)
- Interface interativa e colorida no terminal
- Navegação intuitiva com teclado
- Visualização em tempo real dos projetos
- Suporte a múltiplas operações simultâneas

### Gerenciamento de Projetos
- **Listagem automática** de projetos Claude Code
- **Histórico de acesso** com contadores de visitas
- **Análise de projetos** com métricas detalhadas
- **Exclusão segura** de projetos
- **Limpeza de histórico** para manutenção

### Tecnologias Utilizadas
- **Python 3.8+** - Linguagem principal
- **Textual 0.47.0+** - Framework para TUI moderna
- **Rich 13.7.0+** - Formatação e styling avançado
- **Click 8.1.0+** - Interface de linha de comando
- **UV** - Gerenciador de pacotes rápido

## 📦 Instalação

### Pré-requisitos
- Python 3.8 ou superior
- UV (gerenciador de pacotes Python)

### Passos de Instalação

1. **Clone ou baixe o projeto**
```bash
cd claude-manager
```

2. **Instale as dependências**
```bash
uv sync
```

3. **Execute o aplicativo**
```bash
# Método recomendado - usando o script automatizado
./run.sh

# Método alternativo - execução manual
uv run claude-manager
```

## 🎮 Como Usar

### Interface Principal

Ao executar o `claude-manager`, você verá:

```
┌─────────────────────────────────────────────────────────────────────┐
│ Path                                                          │ Hist │
├─────────────────────────────────────────────────────────────────────┤
│ /Users/agents/Desktop/claude-manager                          │ 4    │
│ /Users/agents/conductor/repo/claude-20x/lusaka               │ 0    │
│ /Users/agents/conductor/repo/claude-20x/tripoli              │ 0    │
└─────────────────────────────────────────────────────────────────────┘
```

### Atalhos de Teclado

| Tecla | Função | Descrição |
|-------|--------|-----------|
| `q` | **Quit** | Sair do aplicativo |
| `a` | **Analyze Projects** | Analisar projetos selecionados |
| `d` | **Delete Project** | Remover projeto da lista |
| `h` | **Clear History** | Limpar histórico de acessos |
| `m` | **MC** | Função de gerenciamento |
| `Ctrl+P` | **Command Palette** | Abrir paleta de comandos |

### Operações Disponíveis

#### 1. Análise de Projetos (`a`)
- Examina a estrutura do projeto
- Gera relatórios de uso
- Identifica configurações
- Mostra estatísticas de desenvolvimento

#### 2. Exclusão de Projetos (`d`)
- Remove projetos da lista de monitoramento
- Operação segura com confirmação
- Mantém integridade dos dados

#### 3. Limpeza de Histórico (`h`)
- Reset dos contadores de visitas
- Limpeza de cache temporário
- Otimização de performance

#### 4. Paleta de Comandos (`Ctrl+P`)
- Acesso rápido a todas as funções
- Busca interativa de comandos
- Atalhos personalizáveis

## 🏗️ Arquitetura do Projeto

### Estrutura de Diretórios
```
claude-manager/
├── src/
│   └── claude_manager/
│       ├── __init__.py
│       ├── cli.py          # Interface de linha de comando
│       ├── config.py       # Gerenciamento de configurações
│       ├── models.py       # Modelos de dados
│       ├── tui.py          # Interface TUI principal
│       ├── ui.py           # Componentes de UI
│       ├── ui_helpers.py   # Utilitários de interface
│       ├── simple_ui.py    # Interface simplificada
│       ├── terminal_utils.py # Utilitários de terminal
│       └── utils.py        # Funções utilitárias
├── tests/                  # Testes automatizados
├── docs/                   # Documentação adicional
├── htmlcov/               # Relatórios de cobertura
├── run.sh                 # 🚀 Script de execução automatizado
├── pyproject.toml         # Configuração do projeto
├── README.md              # Documentação principal
└── CLAUDE_MANAGER_GUIDE.md # Este guia completo
```

### Componentes Principais

#### CLI (`cli.py`)
- Ponto de entrada da aplicação
- Processamento de argumentos
- Inicialização do sistema

#### Configuração (`config.py`)
- Gerenciamento de configurações
- Carregamento de preferências
- Validação de parâmetros

#### Modelos (`models.py`)
- Estruturas de dados
- Validação de tipos
- Serialização/deserialização

#### Interface TUI (`tui.py`)
- Lógica principal da interface
- Gerenciamento de eventos
- Renderização de componentes

## 🔧 Configuração Avançada

### Arquivo de Configuração
O Claude Manager utiliza configurações do Claude Code localizadas em:
- `~/.claude.json` (principal)
- `.claude/settings.json` (projeto específico)

### Personalização da Interface
```python
# Exemplo de configuração personalizada
{
    "theme": "dark",
    "auto_refresh": true,
    "history_limit": 100,
    "project_paths": [
        "~/projects",
        "~/workspace"
    ]
}
```

## 🧪 Desenvolvimento e Testes

### Ambiente de Desenvolvimento
```bash
# Instalar dependências de desenvolvimento
uv sync --dev

# Executar testes
uv run pytest

# Verificar qualidade do código
uv run ruff check
uv run mypy src/

# Formatar código
uv run black src/
uv run isort src/
```

### Estrutura de Testes
- **Testes unitários** - Componentes individuais
- **Testes de integração** - Fluxos completos
- **Testes de interface** - Validação de TUI
- **Cobertura de código** - Relatórios detalhados

## 📊 Métricas e Monitoramento

### Dados Coletados
- **Frequência de uso** por projeto
- **Tempo de sessão** médio
- **Operações mais utilizadas**
- **Performance da interface**

### Análise de Projetos
A funcionalidade de análise (`a`) fornece:
- Contagem de arquivos por tipo
- Estatísticas de desenvolvimento
- Configurações detectadas
- Recomendações de otimização

## 🛠️ Solução de Problemas

### Problemas Comuns

#### Erro de Dependências
```bash
# Limpar cache e reinstalar
uv clean
uv sync
```

#### Interface não Carrega
```bash
# Verificar compatibilidade do terminal
echo $TERM
# Deve suportar cores e caracteres Unicode
```

#### Projetos não Detectados
```bash
# Verificar configuração do Claude Code
cat ~/.claude.json
# Verificar permissões de acesso
```

### Logs e Debug
```bash
# Executar com logs detalhados usando o script
./run.sh --debug

# Executar com logs detalhados manualmente
uv run claude-manager --debug

# Verificar logs do sistema
tail -f ~/.claude/logs/manager.log

# Reset de terminal em caso de problemas
./run.sh --reset-terminal
```

## 🚀 Script de Execução Automatizado

### Funcionalidades do `run.sh`

O script `run.sh` oferece execução simplificada e automatizada:

#### ✨ Características
- **Verificação automática** de dependências
- **Instalação automática** com `uv sync`
- **Execução simplificada** da aplicação
- **Suporte a argumentos** da linha de comando
- **Mensagens coloridas** e informativas
- **Tratamento de erros** robusto

#### 🎯 Modos de Uso

**Execução Básica:**
```bash
./run.sh
```

**Com Argumentos:**
```bash
# Debug mode
./run.sh --debug

# Configuração customizada
./run.sh -c /path/to/config.json

# Sem backup automático
./run.sh --no-backup

# Reset de terminal (emergência)
./run.sh --reset-terminal
```

#### 🔧 Verificações Automáticas

O script automaticamente:
1. **Verifica** se está no diretório correto
2. **Confirma** se o `uv` está instalado
3. **Instala** dependências se necessário
4. **Executa** a aplicação com argumentos fornecidos
5. **Exibe** mensagens de status coloridas

## 🔮 Roadmap e Funcionalidades Futuras

### Versão 2.0 (Planejada)
- [ ] **Integração com Git** - Status de repositórios
- [ ] **Sincronização em nuvem** - Backup de configurações
- [ ] **Plugins customizáveis** - Extensibilidade
- [ ] **Temas personalizáveis** - Aparência configurável

### Versão 2.1 (Planejada)
- [ ] **Dashboard analítico** - Métricas avançadas
- [ ] **Automação de tarefas** - Workflows programáveis
- [ ] **Colaboração em equipe** - Compartilhamento de projetos
- [ ] **API REST** - Integração externa

## 🤝 Contribuição

### Como Contribuir
1. **Fork** do repositório
2. **Clone** sua cópia local
3. **Crie** uma branch para sua feature
4. **Implemente** suas mudanças
5. **Teste** thoroughly
6. **Submeta** um Pull Request

### Padrões de Código
- **PEP 8** compliance
- **Type hints** obrigatórios
- **Docstrings** em todas as funções
- **Testes** para novas funcionalidades

## 📝 Licença

Este projeto está licenciado sob a **MIT License**.

## 📞 Suporte

### Canais de Suporte
- **GitHub Issues**: Para bugs e feature requests
- **Discussions**: Para dúvidas e discussões
- **Email**: consciousness-bridge@proton.me

### Documentação Adicional
- [Claude Code Documentation](https://docs.anthropic.com/claude/docs)
- [Textual Framework Docs](https://textual.textualize.io/)
- [Rich Library Guide](https://rich.readthedocs.io/)

---

*Desenvolvido com ❤️ para a comunidade Claude Code*