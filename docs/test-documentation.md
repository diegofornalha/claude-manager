# Documentação dos Testes - Claude Manager

Este documento descreve todos os testes automatizados do projeto Claude Manager, organizados por módulo e funcionalidade.

## Visão Geral

O projeto possui **43 testes** distribuídos em 4 módulos principais:
- **CLI Tests** (8 testes) - Interface de linha de comando
- **Config Tests** (18 testes) - Gerenciamento de configuração
- **Integration Tests** (7 testes) - Testes de integração
- **Models Tests** (10 testes) - Modelos de dados

## 1. Testes CLI (`test_cli.py`)

### 1.1 `test_version_option`
**Objetivo:** Verifica se a opção `--version` funciona corretamente.
- Executa comando com flag `--version`
- Verifica se o código de saída é 0 (sucesso)
- Confirma se a saída contém "claude-manager" e "1.0.0"

### 1.2 `test_help_option`
**Objetivo:** Testa a exibição da ajuda com `--help`.
- Executa comando com flag `--help`
- Verifica se a saída contém texto de ajuda esperado
- Confirma presença das opções `--config` e `--debug`

### 1.3 `test_main_success`
**Objetivo:** Testa execução bem-sucedida da aplicação principal.
- Simula carregamento de configuração bem-sucedido
- Verifica se a TUI é iniciada corretamente
- Confirma chamadas corretas aos métodos mockados

### 1.4 `test_main_config_load_failure`
**Objetivo:** Testa tratamento de falha no carregamento de configuração.
- Simula falha no carregamento da configuração
- Verifica código de saída 1 (erro)
- Confirma mensagem de erro apropriada

### 1.5 `test_main_keyboard_interrupt`
**Objetivo:** Testa tratamento de interrupção por teclado (Ctrl+C).
- Simula KeyboardInterrupt durante execução da TUI
- Verifica se a aplicação termina graciosamente
- Confirma código de saída 0

### 1.6 `test_main_with_debug`
**Objetivo:** Testa funcionamento com flag de debug.
- Executa com `--debug`
- Verifica se logging de debug é configurado
- Confirma nível de log DEBUG (10)

### 1.7 `test_main_exception_handling`
**Objetivo:** Testa tratamento de exceções gerais.
- Simula exceção durante carregamento
- Verifica código de saída 1
- Confirma mensagem de erro na saída

### 1.8 `test_main_exception_with_debug`
**Objetivo:** Testa tratamento de exceções em modo debug.
- Simula exceção com debug habilitado
- Verifica se stack trace é exibido
- Confirma chamada ao método de impressão de exceção

## 2. Testes de Configuração (`test_config.py`)

### 2.1 `test_init_default_path`
**Objetivo:** Testa inicialização com caminho padrão.
- Verifica se o caminho padrão é `~/.claude.json`
- Confirma criação do diretório de backup
- Testa estrutura de diretórios correta

### 2.2 `test_init_custom_path`
**Objetivo:** Testa inicialização com caminho customizado.
- Usa caminho de configuração específico
- Verifica se o caminho é respeitado

### 2.3 `test_load_config_success`
**Objetivo:** Testa carregamento bem-sucedido de configuração.
- Carrega configuração válida
- Verifica dados carregados corretamente
- Confirma estrutura de projetos

### 2.4 `test_load_config_file_not_found`
**Objetivo:** Testa comportamento quando arquivo não existe.
- Tenta carregar arquivo inexistente
- Verifica retorno False

### 2.5 `test_load_config_invalid_json`
**Objetivo:** Testa tratamento de JSON inválido.
- Cria arquivo com JSON malformado
- Verifica se falha graciosamente

### 2.6 `test_save_config`
**Objetivo:** Testa salvamento de configuração.
- Modifica dados de configuração
- Salva alterações no arquivo
- Verifica persistência dos dados

### 2.7 `test_save_config_with_backup`
**Objetivo:** Testa salvamento com criação de backup.
- Salva configuração com backup habilitado
- Verifica criação do arquivo de backup
- Confirma conteúdo do backup

### 2.8 `test_create_backup`
**Objetivo:** Testa criação manual de backup.
- Cria backup da configuração atual
- Verifica existência e conteúdo do backup
- Confirma nomenclatura correta do arquivo

### 2.9 `test_create_backup_no_config`
**Objetivo:** Testa backup quando configuração não existe.
- Tenta criar backup sem configuração
- Verifica retorno None

### 2.10 `test_clean_old_backups`
**Objetivo:** Testa limpeza de backups antigos.
- Cria 15 backups
- Executa limpeza mantendo apenas 5
- Verifica se os mais recentes foram mantidos

### 2.11 `test_get_projects`
**Objetivo:** Testa recuperação de projetos.
- Obtém lista de projetos
- Verifica quantidade e estrutura
- Confirma conversão para objetos Project

### 2.12 `test_remove_project`
**Objetivo:** Testa remoção de projetos.
- Remove projeto existente
- Tenta remover projeto inexistente
- Verifica comportamento correto em ambos os casos

### 2.13 `test_update_project`
**Objetivo:** Testa atualização de projetos.
- Atualiza projeto existente
- Adiciona novo projeto
- Verifica persistência das alterações

### 2.14 `test_get_config_size`
**Objetivo:** Testa obtenção do tamanho do arquivo de configuração.
- Calcula tamanho do arquivo
- Verifica retorno de valor positivo

### 2.15 `test_get_stats`
**Objetivo:** Testa geração de estatísticas da configuração.
- Obtém estatísticas completas
- Verifica todos os campos calculados
- Confirma valores esperados

### 2.16 `test_restore_from_backup`
**Objetivo:** Testa restauração a partir de backup.
- Cria backup, modifica configuração
- Restaura a partir do backup
- Verifica se dados originais foram recuperados

### 2.17 `test_restore_from_nonexistent_backup`
**Objetivo:** Testa restauração com backup inexistente.
- Tenta restaurar backup que não existe
- Verifica retorno False

### 2.18 `test_get_backups`
**Objetivo:** Testa listagem de backups disponíveis.
- Cria múltiplos backups
- Lista todos os backups
- Verifica ordenação por data

## 3. Testes de Integração (`test_integration.py`)

### 3.1 `test_full_workflow`
**Objetivo:** Testa fluxo completo de operações.
- Carrega configuração com 20 projetos
- Cria backup, remove projetos, salva
- Restaura backup e verifica integridade

### 3.2 `test_project_modifications`
**Objetivo:** Testa modificações complexas em projetos.
- Modifica histórico, servidores MCP e ferramentas
- Salva e recarrega configuração
- Verifica persistência de todas as alterações

### 3.3 `test_backup_rotation`
**Objetivo:** Testa rotação automática de backups.
- Cria 15 backups em sequência
- Verifica se apenas 10 mais recentes são mantidos
- Confirma que os mais novos são preservados

### 3.4 `test_empty_config_handling`
**Objetivo:** Testa tratamento de configuração vazia.
- Carrega arquivo de configuração vazio
- Verifica tratamento gracioso de campos ausentes
- Confirma valores padrão apropriados

### 3.5 `test_concurrent_modifications`
**Objetivo:** Simula modificações concorrentes.
- Modifica múltiplos projetos simultaneamente
- Salva todas as alterações
- Verifica se nenhuma modificação foi perdida

### 3.6 `test_corrupted_config_recovery` (3 variações)
**Objetivo:** Testa recuperação de configurações corrompidas.
- **Truncated:** Arquivo cortado pela metade
- **Invalid JSON:** JSON malformado
- **Wrong Type:** Tipo de dados incorreto
- Verifica recuperação via backup em todos os casos

## 4. Testes de Modelos (`test_models.py`)

### 4.1 `test_project_creation`
**Objetivo:** Testa criação de instância Project.
- Cria projeto com dados completos
- Verifica todos os campos inicializados
- Confirma tipos de dados corretos

### 4.2 `test_history_count`
**Objetivo:** Testa propriedade de contagem de histórico.
- Verifica contagem inicial
- Adiciona entrada e testa nova contagem
- Confirma atualização dinâmica

### 4.3 `test_last_accessed`
**Objetivo:** Testa propriedade de último acesso.
- Verifica último comando executado
- Testa com histórico vazio
- Confirma retorno None quando apropriado

### 4.4 `test_directory_exists`
**Objetivo:** Testa verificação de existência de diretório.
- Testa com diretório existente (True)
- Testa com diretório inexistente (False)
- Verifica comportamento correto da propriedade

### 4.5 `test_get_size_estimate`
**Objetivo:** Testa estimativa de tamanho do projeto.
- Calcula tamanho inicial
- Adiciona dados e recalcula
- Verifica se tamanho aumenta apropriadamente

### 4.6 `test_to_dict`
**Objetivo:** Testa conversão para dicionário.
- Converte projeto para dict
- Verifica todos os campos presentes
- Confirma compatibilidade com JSON

### 4.7 `test_from_dict`
**Objetivo:** Testa criação a partir de dicionário.
- Cria projeto a partir de dados dict
- Verifica todos os campos convertidos
- Confirma tipos e valores corretos

### 4.8 `test_from_dict_with_missing_fields`
**Objetivo:** Testa criação com campos ausentes.
- Usa dicionário vazio
- Verifica aplicação de valores padrão
- Confirma robustez da conversão

### 4.9 `test_roundtrip_conversion`
**Objetivo:** Testa conversão bidirecional (roundtrip).
- Converte projeto para dict e volta
- Verifica se todos os dados são preservados
- Confirma integridade da serialização

## Cobertura de Código

### Módulos com Alta Cobertura (>80%)
- **cli.py:** 100% - Interface completamente testada
- **config.py:** 82.96% - Funcionalidade principal bem coberta
- **models.py:** 100% - Modelos totalmente testados
- **utils.py:** 81.82% - Utilitários adequadamente testados

### Módulos com Baixa Cobertura
- **tui.py:** 16.75% - Interface terminal (UI não testada)
- **ui.py:** 0% - Interface gráfica (UI não testada)
- **simple_ui.py:** 0% - Interface simples (UI não testada)
- **ui_helpers.py:** 0% - Utilitários de UI (não testados)

## Observações sobre Testes

### Pontos Fortes
1. **Cobertura completa da lógica de negócio** - CLI, configuração e modelos
2. **Testes de integração robustos** - Fluxos completos testados
3. **Tratamento de casos extremos** - Arquivos corrompidos, dados ausentes
4. **Fixtures bem organizadas** - Dados de teste reutilizáveis
5. **Testes parametrizados** - Múltiplos cenários cobertos

### Áreas para Melhoria
1. **Interfaces de usuário não testadas** - TUI e UI carecem de testes
2. **Testes de performance** - Não há testes específicos de desempenho
3. **Testes de concorrência real** - Apenas simulação de concorrência
4. **Mocking limitado** - Alguns testes poderiam usar mais mocks

### Estratégia de Teste
O projeto adota uma estratégia focada em **testar a lógica de negócio crítica** enquanto aceita menor cobertura em componentes de interface. Esta é uma abordagem pragmática que maximiza o valor dos testes automatizados.