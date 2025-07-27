# Claude Manager

Uma interface robusta de terminal para gerenciar projetos Claude Code e configurações.

## 📋 Descrição

O Claude Manager é uma ferramenta de linha de comando que oferece uma interface de usuário rica em terminal para gerenciar projetos Claude Code, configurações e fluxos de trabalho de desenvolvimento. Desenvolvido com Python e utilizando bibliotecas modernas como Rich e Textual, oferece uma experiência de usuário intuitiva e eficiente.

## ✨ Características

- **Interface de Terminal Rica**: Interface gráfica moderna usando Rich e Textual
- **Gerenciamento de Projetos**: Criação, configuração e gerenciamento de projetos Claude Code
- **Configurações Flexíveis**: Sistema de configuração robusto com suporte a YAML
- **CLI Intuitivo**: Interface de linha de comando fácil de usar com Click
- **Tipagem Completa**: Suporte completo a type hints para melhor desenvolvimento
- **Testes Abrangentes**: Suite de testes completa com pytest

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- [uv](https://github.com/astral-sh/uv) (recomendado) ou pip

### Instalação com uv (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/ocean1/claude-manager.git
cd claude-manager

# Instale as dependências
uv sync

# Execute o Claude Manager
uv run claude-manager
```

### Instalação com pip

```bash
# Clone o repositório
git clone https://github.com/ocean1/claude-manager.git
cd claude-manager

# Instale o projeto
pip install -e .

# Execute o Claude Manager
claude-manager
```

## 🎯 Uso

### Execução Rápida

```bash
# Usando o script de execução
./run.sh

# Ou diretamente com uv
uv run claude-manager

# Ou com pip
claude-manager
```

### Comandos Disponíveis

```bash
# Mostrar ajuda
claude-manager --help

# Executar com opções específicas
claude-manager [opções]
```

## 🛠️ Desenvolvimento

### Configuração do Ambiente de Desenvolvimento

```bash
# Clone o repositório
git clone https://github.com/ocean1/claude-manager.git
cd claude-manager

# Instale dependências de desenvolvimento
uv sync --extra dev

# Configure pre-commit hooks
pre-commit install
```

### Executando Testes

```bash
# Executar todos os testes
uv run pytest

# Executar testes com cobertura
uv run pytest --cov=claude_manager

# Executar testes específicos
uv run pytest tests/test_cli.py
```

### Linting e Formatação

```bash
# Verificar código com ruff
uv run ruff check .

# Formatar código com black
uv run black .

# Ordenar imports com isort
uv run isort .
```

### Verificação de Tipos

```bash
# Verificar tipos com mypy
uv run mypy claude_manager/
```

## 📁 Estrutura do Projeto

```
claude-manager/
├── claude_manager/          # Código fonte principal
│   ├── __init__.py
│   ├── cli.py              # Interface de linha de comando
│   ├── config.py           # Configurações
│   ├── models.py           # Modelos de dados
│   ├── tui.py              # Interface de terminal
│   ├── ui.py               # Componentes de UI
│   ├── ui_helpers.py       # Helpers de UI
│   ├── simple_ui.py        # UI simplificada
│   ├── terminal_utils.py   # Utilitários de terminal
│   └── utils.py            # Utilitários gerais
├── tests/                  # Testes
├── docs/                   # Documentação
├── pyproject.toml          # Configuração do projeto
├── run.sh                  # Script de execução
└── README.md               # Este arquivo
```

## 🤝 Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

### Padrões de Código

- Siga as convenções PEP 8
- Use type hints em todas as funções
- Escreva testes para novas funcionalidades
- Mantenha a cobertura de testes acima de 80%

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 👥 Autores

- **Claude Manager Contributors** - [consciousness-bridge@proton.me](mailto:consciousness-bridge@proton.me)

## 🐛 Reportando Bugs

Se você encontrar um bug, por favor abra uma issue no GitHub com:

- Descrição detalhada do bug
- Passos para reproduzir
- Comportamento esperado vs. atual
- Informações do sistema (OS, versão do Python, etc.)

## 📞 Suporte

Para suporte e perguntas:

- Abra uma issue no GitHub
- Entre em contato: [consciousness-bridge@proton.me](mailto:consciousness-bridge@proton.me)

---

**Claude Manager** - Gerenciando projetos Claude Code com eficiência e estilo! 🚀 