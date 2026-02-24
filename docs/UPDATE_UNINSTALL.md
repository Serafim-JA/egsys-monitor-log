# egSYS Monitor - Sistema de Gerenciamento

## 🔄 Auto-Atualização

O sistema verifica automaticamente por atualizações no GitHub.

### Verificar Atualizações

```bash
egsys-update
```

### Como Funciona

1. Conecta ao GitHub API
2. Compara versão local com versão mais recente
3. Se houver atualização, faz `git pull`
4. Preserva configurações do usuário
5. Atualiza arquivo VERSION

### Configuração

- **Repositório:** `Serafim-JA/egsys-monitor-log`
- **Verificação:** Manual via comando
- **Backup:** Configurações preservadas automaticamente

---

## 🗑️ Desinstalação

Remove completamente o aplicativo do sistema.

### Desinstalar

```bash
egsys-uninstall
```

### O que é Removido

✓ Arquivos da aplicação  
✓ Configurações  
✓ Logs  
✓ Atalhos do sistema  
✓ Serviços systemd  
✓ Entradas no .bashrc  

### Confirmação

Para confirmar, digite: `DESINSTALAR`

---

## 📋 Comandos Disponíveis

```bash
egsys-monitor        # Iniciar aplicação
egsys-update         # Verificar/aplicar atualizações
egsys-uninstall      # Desinstalar completamente
```

---

## 🔍 Detecção de Instalação

O desinstalador procura automaticamente em:
- `~/egSYS-Monitor`
- `~/.egsys-monitor`
- `~/Documentos/egSYS-Monitor`

---

## 🛡️ Segurança

- Backup automático de configurações antes de atualizar
- Confirmação obrigatória para desinstalar
- Rollback automático em caso de falha
