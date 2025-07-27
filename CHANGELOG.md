# Changelog

Todas as mudanças notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/),
e este projeto adere ao [Semantic Versioning](https://semver.org/lang/pt-BR/).

## [Unreleased]

### 🚀 Novidades

#### Sistema de Agentes Avançado
- **Novo modelo de dados `Agent`** com suporte completo para:
  - Padrões neurais (`neural_patterns`)
  - Aprendizado habilitado (`learning_enabled`)
  - Memória coletiva (`collective_memory`)
  - Papel no Hive Mind (`hive_mind_role`)
  - Execução concorrente (`concurrent_execution`)
  - Integração SPARC (`sparc_integration`)
- **Agentes pré-configurados**:
  - `self-improving`: Agente auto-aprimorável com aprendizado adaptativo
  - `subagent-expert`: Especialista em criar e otimizar sub-agentes
- **Parsing YAML aprimorado** para frontmatter de agentes em arquivos Markdown
- **Suporte para agentes globais e de projeto** com diferenciação clara

#### Interface TUI (Terminal User Interface)
- **Nova tela de gerenciamento de agentes** acessível por tecla `g`
- **Tradução completa para português** de toda interface
- **Visualização aprimorada** com indicadores visuais para:
  - Agentes avançados com padrões neurais
  - Status de prioridade (high/medium/low)
  - Cores personalizadas por agente

#### Sistema de Configuração
- **Método `parse_agent_file`** para extrair configurações de agentes Markdown
- **Método `scan_agents_directory`** para descoberta automática de agentes
- **Validação robusta** de dados YAML com tratamento de erros

#### Documentação Completa
- **Nova estrutura de documentação** organizada em clusters funcionais:
  - Sistema de Agentes (`agent-system.md`)
  - Interfaces de Usuário (`user-interfaces.md`)
  - CLI e Utilitários (`cli-utilities.md`)
  - Configuração e Dados (`configuration-data-management.md`)
  - Sistema de Aceitação de Confiança (`trust-acceptance-system.md`)
- **Índice principal** (`index.md`) com navegação clara
- **Documentação técnica detalhada** para cada módulo

### 🔧 Melhorias

#### Performance e Estabilidade
- **Parsing YAML mais robusto** com tratamento de exceções específicas
- **Melhor gestão de memória** para projetos grandes
- **Cache otimizado** para leitura de arquivos de agentes

#### Interface de Usuário
- **Navegação aprimorada** com teclas de atalho consistentes
- **Feedback visual melhorado** para operações longas
- **Mensagens de erro mais claras** e informativas
- **Suporte aprimorado para temas** com cores personalizáveis

#### Segurança
- **Sistema de Aceitação de Confiança** mais granular
- **Validação aprimorada** de configurações de agentes
- **Proteção contra injeção** em parsing YAML

#### Compatibilidade
- **Suporte melhorado para diferentes sistemas operacionais**
- **Compatibilidade com Python 3.8+** garantida
- **Dependências atualizadas** para versões mais recentes

### 🐛 Correções

#### Parsing de Configuração
- Corrigido erro ao processar arquivos YAML mal formatados
- Resolvido problema com caminhos relativos em Windows
- Tratamento correto de caracteres especiais em nomes de agentes

#### Interface TUI
- Corrigido vazamento de memória em atualizações frequentes
- Resolvido problema de renderização em terminais pequenos
- Correção de encoding UTF-8 em sistemas não-UTF8

#### Sistema de Arquivos
- Corrigido erro ao criar diretórios de backup em sistemas com permissões restritas
- Resolvido problema com links simbólicos em projetos
- Tratamento correto de arquivos grandes (>10MB)

### 📝 Mudanças Internas

- Refatoração completa do módulo `config.py` para melhor separação de responsabilidades
- Adição de type hints em todos os métodos públicos
- Melhoria na cobertura de testes (>90%)
- Atualização de todas as dependências para versões estáveis

### ⚠️ Mudanças Quebradas

- O formato de configuração de agentes mudou de JSON para YAML com frontmatter
- Algumas teclas de atalho foram alteradas para consistência
- API interna de `ClaudeConfigManager` foi reorganizada

---

## Como Atualizar

1. Faça backup do seu arquivo `~/.claude.json`
2. Atualize o Claude Manager: `pip install -U claude-manager`
3. Execute `claude-manager --migrate` para migrar configurações antigas
4. Revise as novas funcionalidades em `claude-manager --help`

## Próximas Versões

### Planejado para v1.1.0
- [ ] Integração com Claude Flow MCP
- [ ] Sistema de templates para agentes
- [ ] Exportação/importação de configurações
- [ ] Modo colaborativo multi-usuário

### Planejado para v1.2.0
- [ ] Interface web opcional
- [ ] API REST para integração
- [ ] Plugins personalizados
- [ ] Métricas avançadas de uso