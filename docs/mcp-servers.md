# MCP Servers - Model Context Protocol

## Visão Geral

O Claude Manager suporta a configuração e gerenciamento de servidores MCP (Model Context Protocol) **locais específicos para cada projeto**. O MCP é um protocolo que permite que o Claude Code se conecte a ferramentas e serviços externos, expandindo suas capacidades.

### Foco em Servidores Locais (stdio)

O Claude Manager **intencionalmente** suporta apenas servidores MCP locais (transporte stdio) porque:

- **Organização por Projeto**: Cada projeto tem seus próprios servidores MCP específicos
- **Contexto Claro**: Você sabe exatamente quais servidores estão ativos para cada projeto
- **Sem Interferência**: Elimina confusão com servidores remotos globais (HTTP/SSE)
- **Gerenciamento Simples**: Foco em ferramentas locais relacionadas ao projeto específico

> **Nota**: Servidores remotos (HTTP/SSE) são globais e devem ser configurados diretamente no Claude Code com `claude mcp add --transport http`.

## O que são Servidores MCP?

Servidores MCP são componentes que fornecem funcionalidades adicionais ao Claude Code através de:

- **Ferramentas (Tools)**: Ações que o Claude pode executar
- **Recursos (Resources)**: Dados e informações que o Claude pode acessar
- **Prompts**: Modelos de prompt predefinidos para tarefas específicas

## Configurando Servidores MCP

### Via Interface TUI

1. Abra o Claude Manager: `./run.sh`
2. Selecione um projeto e pressione `m` para gerenciar servidores MCP
3. Use as seguintes opções:
   - `a`: Adicionar novo servidor
   - `e`: Editar servidor existente
   - `d`: Deletar servidor
   - `t`: Alternar ativação de todos os servidores

### Via Interface UI

1. Execute o Claude Manager
2. Escolha "Manage MCP Servers" no menu principal
3. Selecione o projeto desejado
4. Configure os servidores conforme necessário

## Formato de Configuração

Os servidores MCP são configurados no formato JSON. Exemplo básico:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": {
    "WORKSPACE_DIR": "/path/to/workspace"
  }
}
```

### Campos de Configuração

- **command** (obrigatório): O comando executável do servidor
- **args** (opcional): Array de argumentos para o comando
- **env** (opcional): Variáveis de ambiente para o servidor

## Exemplos de Servidores MCP

### 1. Servidor de Sistema de Arquivos

Permite acesso controlado ao sistema de arquivos:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-filesystem"],
  "env": {
    "WORKSPACE_DIR": "/home/user/projects"
  }
}
```

### 2. Claude Flow MCP

Adiciona capacidades avançadas de coordenação e swarm:

```json
{
  "command": "npx",
  "args": ["claude-flow@alpha", "mcp", "start"]
}
```

### 3. Servidor GitHub

Integração com repositórios GitHub:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_TOKEN": "ghp_your_token_here"
  }
}
```

### 4. Servidor de Banco de Dados

Acesso a bancos de dados SQL:

```json
{
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-postgres"],
  "env": {
    "DATABASE_URL": "postgresql://user:pass@localhost/db"
  }
}
```

## Gerenciamento de Servidores

### Habilitar/Desabilitar Todos os Servidores

Cada projeto tem uma opção para habilitar ou desabilitar todos os servidores MCP de uma vez:

- **Via TUI**: Pressione `t` na tela de gerenciamento MCP
- **Via UI**: Use a opção "Enable/disable all MCP servers"

### Servidores Específicos vs Globais

- **Servidores de Projeto**: Configurados individualmente para cada projeto
- **Servidores Globais**: Podem ser habilitados através das listas:
  - `enabled_mcpjson_servers`: Lista de servidores globais habilitados
  - `disabled_mcpjson_servers`: Lista de servidores globais desabilitados

## Boas Práticas

### 1. Segurança

- **Tokens e Senhas**: Use variáveis de ambiente do sistema em vez de hardcode
- **Permissões**: Configure apenas o acesso mínimo necessário
- **Validação**: Sempre valide as configurações JSON antes de salvar

### 2. Performance

- **Servidores Mínimos**: Ative apenas os servidores necessários
- **Recursos**: Monitore o uso de recursos dos servidores
- **Timeouts**: Configure timeouts apropriados para operações longas

### 3. Organização

- **Nomes Descritivos**: Use nomes que indiquem a função do servidor
- **Documentação**: Mantenha notas sobre a configuração de cada servidor
- **Versionamento**: Considere versionar suas configurações MCP

## Integração com Claude Code

Uma vez configurados, os servidores MCP ficam disponíveis automaticamente no Claude Code quando você abre o projeto. O Claude Code:

1. Carrega as configurações do projeto
2. Inicia os servidores MCP configurados
3. Disponibiliza as ferramentas e recursos para uso

## Solução de Problemas

### Servidor não inicia

1. Verifique se o comando está instalado: `which npx` ou `which [comando]`
2. Valide o JSON de configuração
3. Verifique as variáveis de ambiente necessárias
4. Consulte os logs do Claude Code para erros

### Ferramentas não aparecem

1. Confirme que o servidor está configurado corretamente
2. Verifique se `enable_all_project_mcp_servers` está ativado
3. Reinicie o Claude Code após mudanças na configuração

### Problemas de Permissão

1. Verifique as permissões de arquivo/diretório
2. Confirme que tokens de API estão válidos
3. Teste o comando manualmente no terminal

## Recursos Adicionais

- [Documentação oficial do MCP](https://modelcontextprotocol.io/docs)
- [Lista de servidores MCP disponíveis](https://github.com/modelcontextprotocol/servers)
- [Criando seu próprio servidor MCP](https://modelcontextprotocol.io/docs/server-development)

## Próximos Passos

1. Explore os servidores MCP disponíveis
2. Configure servidores relevantes para seus projetos
3. Experimente criar integrações customizadas
4. Compartilhe suas configurações com a comunidade