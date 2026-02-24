# egSYS Monitor - Instalador Executável

Instalador interativo estilo Discord com interface TUI completa.

## 🎯 Características

- ✅ Interface TUI profissional com logo egSYS
- ✅ Tela de boas-vindas
- ✅ Aceitação de licença
- ✅ Seleção de diretório customizável
- ✅ Barra de progresso animada
- ✅ Instalação automática de dependências
- ✅ Criação de atalhos do sistema
- ✅ Executável standalone (.exec)

## 🔨 Gerar Executável

```bash
cd installer
bash build.sh
```

Isso criará: `dist/egsys-monitor-installer`

## 🚀 Usar Instalador

### Opção 1: Python (desenvolvimento)
```bash
python3 egsys_installer.py
```

### Opção 2: Executável (produção)
```bash
./dist/egsys-monitor-installer
```

## 📋 Fluxo de Instalação

1. **Tela de Boas-vindas**
   - Logo egSYS em ASCII art
   - Lista de recursos
   - Pressione ENTER para continuar

2. **Licença**
   - Termos MIT License
   - Aceitar [S/N]

3. **Diretório**
   - Padrão: `~/.egsys-monitor`
   - Customizável pelo usuário
   - Confirmação antes de instalar

4. **Instalação**
   - Barra de progresso animada
   - 6 etapas com feedback visual
   - Instalação automática

5. **Conclusão**
   - Resumo da instalação
   - Instruções de uso
   - Opção de iniciar imediatamente

## 📦 O que é Instalado

```
~/.egsys-monitor/
├── src/              # Código fonte
├── config/           # Configurações
├── logs/             # Logs do sistema
└── .env              # Variáveis de ambiente

~/.local/bin/
└── egsys-monitor     # Atalho executável
```

## 🎨 Interface

```
        ███████╗ ██████╗ ███████╗██╗   ██╗███████╗
        ██╔════╝██╔════╝ ██╔════╝╚██╗ ██╔╝██╔════╝
        █████╗  ██║  ███╗███████╗ ╚████╔╝ ███████╗
        ██╔══╝  ██║   ██║╚════██║  ╚██╔╝  ╚════██║
        ███████╗╚██████╔╝███████║   ██║   ███████║
        ╚══════╝ ╚═════╝ ╚══════╝   ╚═╝   ╚══════╝

           Monitor de Logs Distribuídos
                    v1.0.0

╔══════════════════════════════════════════════════════════════╗
║              Instalador egSYS Monitor                        ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║ Bem-vindo ao instalador do egSYS Monitor!                   ║
║                                                              ║
║ Este assistente irá guiá-lo através da instalação.          ║
║                                                              ║
║ ✓ Monitor de logs SSH em tempo real                         ║
║ ✓ Dashboard web com autenticação                            ║
║ ✓ Interface de terminal interativa                          ║
║ ✓ Suporte a múltiplos servidores                            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

## 🔧 Dependências

O instalador instala automaticamente:
- paramiko
- python-dotenv
- rich
- flask
- bcrypt
- gunicorn

## 📝 Notas

- Requer Python 3.8+
- Funciona em Linux/macOS
- Executável tem ~50MB
- Instalação leva ~30 segundos
