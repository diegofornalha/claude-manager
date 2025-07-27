# Sistema de Aceitação de Confiança - Claude Manager

## 📋 Visão Geral

O **Sistema de Aceitação de Confiança** é um mecanismo de segurança fundamental do Claude Code que o Claude Manager utiliza para gerenciar e monitorar a confiabilidade dos projetos. Este sistema garante que apenas projetos explicitamente aprovados pelo usuário possam executar operações privilegiadas.

## 🔒 Conceito de Segurança

### O que é Aceitação de Confiança?

A aceitação de confiança é um **gate de segurança** que requer aprovação explícita do usuário antes de permitir que um projeto Claude Code execute certas operações. É uma medida de proteção contra execução acidental de código não confiável.

### Por que é Importante?

- **Segurança**: Protege contra execução de código malicioso
- **Controle**: Usuário decide quais projetos são confiáveis
- **Transparência**: Status de confiança sempre visível
- **Auditoria**: Rastreamento completo de permissões

## 🏗️ Implementação Técnica

### Modelo de Dados

```python
@dataclass
class Project:
    """Represents a Claude Code project."""
    
    path: str
    has_trust_dialog_accepted: bool = False  # ← Campo de confiança
    # ... outros campos
```

### Estrutura no JSON de Configuração

```json
{
  "projects": {
    "/path/to/project": {
      "hasTrustDialogAccepted": true,
      "allowedTools": ["tool1", "tool2"],
      "history": [...],
      // ... outras configurações
    }
  }
}
```

## 🎯 Funcionalidades do Claude Manager

### 1. Análise de Projetos

O Claude Manager analisa automaticamente todos os projetos e identifica aqueles sem aceitação de confiança:

```python
# Código da análise (claude_manager/tui.py:541-580)
def on_mount(self) -> None:
    projects = self.config_manager.get_projects()
    
    # Coleta projetos sem confiança
    no_trust = []
    for path, project in projects.items():
        if not project.has_trust_dialog_accepted:
            no_trust.append(path)
    
    # Gera relatório
    if no_trust:
        report.append(
            f"[bold orange]Projetos sem aceitação de confiança ({len(no_trust)}):[/bold orange]"
        )
        for path in no_trust[:10]:
            report.append(f"  • {path}")
```

### 2. Exibição de Status

Na tela de detalhes do projeto, o status é exibido claramente:

```python
# Código de exibição (claude_manager/tui.py:240-241)
f"Confiança aceita: {'✓' if self.project.has_trust_dialog_accepted else '✗'}\n"
```

### 3. Gerenciamento de Status

Permite alternar o status de confiança através da interface:

```python
# Código de edição (claude_manager/ui.py:400-410)
elif action == "toggle_trust":
    project.has_trust_dialog_accepted = not project.has_trust_dialog_accepted
    self.config_manager.update_project(project)
    if self.config_manager.save_config():
        status = "accepted" if project.has_trust_dialog_accepted else "not accepted"
        console.print(f"[green]Trust dialog is now {status}.[/green]")
```

## 🖥️ Interface do Usuário

### Análise de Projetos

```
🟠 Projetos sem aceitação de confiança (1):
  • /Users/agents/conductor/repo/claude-manager/guangzhou
```

### Detalhes do Projeto

```
Diretório existe: ✓
Entradas do histórico: 15
Servidores MCP: 2
Confiança aceita: ✗  ← Status visível
Tamanho: 2.3KB
```

### Menu de Edição

```
┌─ Configurações do Projeto ──────────────────┐
│ Directory Exists: ✓                         │
│ History Entries: 15                         │
│ MCP Servers: 2                              │
│ Trust Dialog Accepted: ✗                    │
│ Allowed Tools: 3                            │
│ Ignore Patterns: 2                          │
└─────────────────────────────────────────────┘

O que você gostaria de fazer?
❯ Toggle Trust Dialog  ← Opção para alternar
  Clear History
  Edit Allowed Tools
  Edit Ignore Patterns
  View Full Details
  Back to Main Menu
```

## 🚀 Como Usar

### 1. Verificar Status de Confiança

```bash
# Execute o Claude Manager
claude-manager

# Navegue para Análise de Projetos
# Pressione 'a' na tela principal
```

### 2. Alternar Status de Confiança

```bash
# Na lista de projetos, selecione um projeto
# Pressione 'Enter' para ver detalhes
# Escolha "Editar Projeto"
# Selecione "Toggle Trust Dialog"
```

### 3. Monitoramento Contínuo

O Claude Manager mostra automaticamente:
- Quantos projetos não têm aceitação de confiança
- Quais projetos específicos precisam de atenção
- Status atual de cada projeto

## 🔍 Casos de Uso

### Cenário 1: Projeto Novo
```
Situação: Projeto recém-criado sem aceitação de confiança
Ação: Usuário aceita confiança para habilitar funcionalidades completas
Resultado: Projeto pode executar operações privilegiadas
```

### Cenário 2: Projeto Suspeito
```
Situação: Projeto de fonte não confiável
Ação: Usuário mantém status "não confiável"
Resultado: Funcionalidades limitadas por segurança
```

### Cenário 3: Auditoria de Segurança
```
Situação: Verificação de todos os projetos
Ação: Usar análise do Claude Manager
Resultado: Lista completa de projetos e seus status
```

## ⚙️ Configuração Avançada

### Backup Automático

O Claude Manager faz backup automático das configurações de confiança:

```bash
# Backup é criado automaticamente em:
~/.claude.json.backup
```

### Restauração

```bash
# Para restaurar configurações:
claude-manager
# → Gerenciar Backups → Restaurar Backup
```

## 🛡️ Boas Práticas

### 1. Revisão Regular
- Use a análise de projetos semanalmente
- Verifique projetos sem aceitação de confiança
- Mantenha apenas projetos confiáveis aprovados

### 2. Aceitação Seletiva
- Aceite confiança apenas em projetos conhecidos
- Revogue confiança de projetos suspeitos
- Documente decisões de confiança

### 3. Monitoramento
- Configure alertas para novos projetos
- Revise histórico de mudanças
- Mantenha backup das configurações

## 🔧 Solução de Problemas

### Projeto Não Aparece na Lista
```bash
# Verifique se o projeto está na configuração
cat ~/.claude.json | grep "hasTrustDialogAccepted"

# Recarregue a configuração no Claude Manager
# Pressione 'r' para refresh
```

### Status Não Salva
```bash
# Verifique permissões do arquivo
ls -la ~/.claude.json

# Force backup e tente novamente
# O Claude Manager faz backup automático
```

### Muitos Projetos Sem Confiança
```bash
# Use a análise para identificar todos
# Revise cada projeto individualmente
# Aceite apenas projetos necessários
```

## 📊 Métricas e Relatórios

### Estatísticas Disponíveis
- Total de projetos
- Projetos com/sem aceitação de confiança
- Histórico de mudanças
- Tamanho das configurações

### Exemplo de Relatório
```
Resumo:
Total de projetos: 5
Projetos com confiança aceita: 3
Projetos sem confiança aceita: 2
Taxa de aceitação: 60%
```

## 🔮 Futuras Melhorias

### Funcionalidades Planejadas
- [ ] Notificações automáticas para novos projetos
- [ ] Políticas de confiança baseadas em padrões
- [ ] Integração com sistemas de segurança
- [ ] Relatórios detalhados de auditoria
- [ ] Backup em nuvem das configurações

### APIs e Integração
- [ ] API REST para gerenciamento programático
- [ ] Webhooks para notificações
- [ ] Integração com ferramentas de segurança
- [ ] Exportação de relatórios

## 📚 Referências

### Documentação Relacionada
- [Claude Code Security](https://docs.anthropic.com/claude/docs/security)
- [MCP Server Security](https://modelcontextprotocol.io/docs/security)
- [Project Configuration](https://docs.anthropic.com/claude/docs/project-config)

### Arquivos do Código
- `claude_manager/models.py` - Modelo de dados
- `claude_manager/tui.py` - Interface de análise
- `claude_manager/ui.py` - Gerenciamento de status
- `claude_manager/config.py` - Configuração

---

**Sistema de Aceitação de Confiança** - Mantendo seus projetos Claude Code seguros e controlados! 🔒✨ 