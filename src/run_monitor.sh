#!/bin/bash

# ==============================================================================
#  egSYS MONITOR - ENTERPRISE EDITION v7.0 (ALL LOGS ENABLED)
# ==============================================================================
#  Autor: Lucas Serafim & Equipe
#  Funcionalidades: Monitoramento Total, Auditoria, SSH Key Manager, Auto-Update
# ==============================================================================

# --- CONFIGURAÇÕES ---
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIT_FILE="$BASE_DIR/audit_egsys.log"
VERSION="7.0.0"

# Cores e Estilos
RED='\033[0;31m'; GREEN='\033[0;32m'; BLUE='\033[0;34m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; MAGENTA='\033[0;35m'; WHITE='\033[1;37m'; BOLD='\033[1m'
NC='\033[0m'

# Variáveis de Sessão
CURRENT_USER=""
DEBUG_MODE=0

# --- CREDENCIAIS ---
USER_PR_MOB=gabriel.egsys; HOST_PR_MOB=201.77.18.195; PASSWORD_PR_MOB='#include<Celepar2024>'
USER_PR_MOB2=gabriel.egsys; HOST_PR_MOB2=201.77.18.206; PASSWORD_PR_MOB2='#include<Celepar2024>'
USER_PR_MOB3=gabriel.egsys; HOST_PR_MOB3=201.77.18.207; PASSWORD_PR_MOB3='#include<Celepar2024>'
USER_SC_MOB=egsys; HOST_SC_MOB=200.19.221.184; PASSWORD_SC_MOB='Mobile#194mb'
USER_SC_WEB=egsys; HOST_SC_WEB=200.19.221.191; PASSWORD_SC_WEB='Sade#195app'
USER_RO_MOB=suporte; HOST_RO_MOB=172.16.112.4; PASSWORD_RO_MOB='UnSKgiOEfgXwROqqg5pmA6UmruNq'
USER_TO_MOB=pmlrpmobile; HOST_TO_MOB=10.48.209.52; PASSWORD_TO_MOB='6M#b96C8'
USER_GM_MOB=egsys-admin; HOST_GM_MOB=45.7.171.132; PASSWORD_GM_MOB='aYlnOYnLzlH81f5a'
USER_GM_AIT=root; HOST_GM_AIT=159.65.164.82; PASSWORD_GM_AIT='Nexus!00*99#'
USER_PI_WEB_MOB=root; HOST_PI_WEB_MOB=200.23.153.183; PASSWORD_PI_WEB_MOB='qgI4ahmno4,^Gnp'

# --- BANCO DE DADOS DE LOGS (COMPLETO) ---
# Formato: "CLIENTE|SERVIDOR|CATEGORIA|NOME_LOG|COMANDO"

declare -a LOG_DATA=(
    # --- PARANÁ (PR) ---
    # Mobile 1
    "pr|mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/Mobile/PM_Socket.log"
    "pr|mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/Mobile/PM_Consumidor.log"
    "pr|mob|logs_mobile|consumidor_baixa|tail -f /var/egsys-file/log/java/Mobile/PM_ConsumidorBaixaPrioridade.log"
    "pr|mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/Mobile/PM_Generator.log"
    "pr|mob|logs_mobile|gerador2|tail -f /var/egsys-file/log/java/Mobile/PM_Generator2.log"
    "pr|mob|logs_mobile|gerador3|tail -f /var/egsys-file/log/java/Mobile/PM_Generator3.log"
    "pr|mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/Mobile/PM_SocketFiles.log"
    "pr|mob|logs_mobile|controle_frames|tail -f /var/egsys-file/log/java/Mobile/PM_ControleFrames.log"
    "pr|mob|logs_provider|provider|tail -f /var/egsys-file/log/java/Provider/GlobalProvider.log"
    "pr|mob|logs_store|socket|tail -f /var/egsys-file/log/java/Store/Store_Socket.log"
    "pr|mob|logs_gestao|socket|tail -f /var/egsys-file/log/java/Gestao/Gestao_Socket.log"
    "pr|mob|logs_gestao|gerador|tail -f /var/egsys-file/log/java/Gestao/Gestao_Gerador.log"
    "pr|mob|logs_gestao|notificador|tail -f /var/egsys-file/log/java/Gestao/Gestao_Notificador.log"
    # Mobile 3 (Gestão Dedicada)
    "pr|mob3|logs_gestao|api|tail -f /var/egsys-docker/containers/syspm-gestao-api-docker/service/build/logs/ws-gestao.log"
    "pr|mob3|logs_gestao|alerta|tail -f /var/egsys-docker/containers/syspm-gestao-alerta-worker-docker/service/build/logs/gestao-gerenciador-alerta.log.log"
    "pr|mob3|logs_gestao|notificador|tail -f /var/egsys-docker/containers/syspm-gestao-notificador-worker-docker/service/build/logs/gestao-notificador-alerta.log"

    # --- SANTA CATARINA (SC) ---
    # Mobile
    "sc|mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/Mobile/PMSC_Socket.log"
    "sc|mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/Mobile/PMSC_ConsumidorDefault.log"
    "sc|mob|logs_mobile|consumidor_baixa|tail -f /var/egsys-file/log/java/Mobile/PMSC_ConsumidorBaixaPrioridade.log"
    "sc|mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/Mobile/PMSC_Generator.log"
    "sc|mob|logs_mobile|gerador2|tail -f /var/egsys-file/log/java/Mobile/PMSC_Generator2.log"
    "sc|mob|logs_mobile|gerador3|tail -f /var/egsys-file/log/java/Mobile/PMSC_Generator3.log"
    "sc|mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/Mobile/PMSC_SocketFiles.log"
    "sc|mob|logs_mobile|controle_frames|tail -f /var/egsys-file/log/java/Mobile/PMSC_ControleFrames.log"
    "sc|mob|logs_ait|socket|tail -f /var/egsys-file/log/java/AIT/AIT_Socket.log"
    "sc|mob|logs_ait|gerador|tail -f /var/egsys-file/log/java/AIT/AIT_Gerador.log"
    "sc|mob|logs_ait|consumidor|tail -f /var/egsys-file/log/java/AIT/AIT_Consumidor.log"
    # Web (Sade)
    "sc|web|logs_sade|access|tail -f /var/egsys-docker/volumes/php7.3-apache/log/sade.pm.sc.gov.br.access.log"
    "sc|web|logs_sade|access_ssl|tail -f /var/egsys-docker/volumes/php7.3-apache/log/sade.pm.sc.gov.br.access-ssl.log"
    "sc|web|logs_sade|error|tail -f /var/egsys-docker/volumes/php7.3-apache/log/sade.pm.sc.gov.br.error.log"
    "sc|web|logs_sade|error_ssl|tail -f /var/egsys-docker/volumes/php7.3-apache/log/sade.pm.sc.gov.br.error-ssl.log"

    # --- RONDÔNIA (RO) ---
    "ro|mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/Mobile/Socket.log"
    "ro|mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/Mobile/PMRO_Consumidor.log"
    "ro|mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/Mobile/PMRO_Gerador.log"
    "ro|mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/Mobile/PMRO_SocketFiles.log"
    "ro|mob|logs_mobile|notificador|tail -f /var/egsys-file/log/java/Mobile/PM_Notificador.log"
    "ro|mob|logs_ait|socket|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Socket.log"
    "ro|mob|logs_ait|gerador|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Generator.log"
    "ro|mob|logs_ait|consumidor|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Consumer.log"
    "ro|mob|logs_ait|socket_runtime|tail -f /var/egsys-file/log/java/SYSAIT/SYS_SocketRunTime.log"
    "ro|mob|logs_ait|uploadfile|tail -f /var/egsys-file/log/java/SYSAIT/SYS_UploadFile.log"
    "ro|mob|logs_store|socket|tail -f /var/egsys-file/log/java/Store/Store_Socket.log"
    "ro|mob|logs_gestao|socket|tail -f /var/egsys-file/log/java/Store/Gestao_Socket.log"
    "ro|mob|logs_gestao|gerador|tail -f /var/egsys-file/log/java/Store/Gestao_Gerador.log"
    "ro|mob|logs_gestao|notificador|tail -f /var/egsys-file/log/java/Store/Gestao_Notificador.log"
    "ro|mob|logs_provider|provider|tail -f /var/egsys-file/log/java/Provider/GlobalProvider.log"
    "ro|mob|logs_email|sender|tail -f /var/egsys-file/log/java/Email/EmailSender.log"
    "ro|mob|logs_email|gerador|tail -f /var/egsys-file/log/java/Email/EmailSenderGenerator.log"

    # --- TOCANTINS (TO) ---
    "to|mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/Mobile/PM_Socket.log"
    "to|mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/Mobile/PM_Generator.log"
    "to|mob|logs_mobile|gerador2|tail -f /var/egsys-file/log/java/Mobile/PM_Generator2.log"
    "to|mob|logs_mobile|gerador3|tail -f /var/egsys-file/log/java/Mobile/PM_Generator3.log"
    "to|mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/Mobile/PM_Consumidor.log"
    "to|mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/Mobile/PM_SocketFiles.log"
    "to|mob|logs_ait|socket|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Socket.log"
    "to|mob|logs_ait|gerador|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Generator.log"
    "to|mob|logs_ait|gerador2|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Generator2.log"
    "to|mob|logs_ait|gerador3|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Generator3.log"
    "to|mob|logs_ait|consumidor|tail -f /var/egsys-file/log/java/SYSAIT/SYS_Consumidor.log"
    "to|mob|logs_ait|socket_files|tail -f /var/egsys-file/log/java/SYSAIT/SYS_SocketFiles.log"
    "to|mob|logs_store|socket|tail -f /var/egsys-file/log/java/Store/Store_Socket.log"
    "to|mob|logs_gestao|socket|tail -f /var/egsys-file/log/java/Store/Gestao_Socket.log"
    "to|mob|logs_gestao|gerador|tail -f /var/egsys-file/log/java/Store/Gestao_Gerador.log"
    "to|mob|logs_gestao|notificador|tail -f /var/egsys-file/log/java/Store/Gestao_Notificador.log"
    "to|mob|logs_provider|provider|tail -f /var/egsys-file/log/java/Provider/GlobalProvider.log"
    "to|mob|logs_email|sender|tail -f /var/egsys-file/log/java/Email/EmailSender.log"
    "to|mob|logs_email|gerador|tail -f /var/egsys-file/log/java/Email/EmailSenderGenerator.log"

    # --- GUARDA MUNICIPAL (GM) ---
    "gm|mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/siseg_gm/socket.log"
    "gm|mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/siseg_gm/generator.log"
    "gm|mob|logs_mobile|gerador2|tail -f /var/egsys-file/log/java/siseg_gm/generator2.log"
    "gm|mob|logs_mobile|gerador3|tail -f /var/egsys-file/log/java/siseg_gm/generator3.log"
    "gm|mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/siseg_gm/consumidor.log"
    "gm|mob|logs_mobile|consumidor_baixa|tail -f /var/egsys-file/log/java/siseg_gm/consumidor_baixa_prioridade.log"
    "gm|mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/siseg_gm/socket_files.log"
    "gm|mob|logs_mobile|store_socket|tail -f /var/egsys-file/log/java/siseg_gm/store_socket.log"
    "gm|mob|logs_mobile|controle_frames|tail -f /var/egsys-file/log/java/siseg_gm/controle_frames.log"
    "gm|mob|logs_ait|socket|tail -f /var/egsys-file/log/java/SYSAIT/PM_Socket.log"
    "gm|mob|logs_ait|gerador|tail -f /var/egsys-file/log/java/SYSAIT/PM_Generator.log"
    "gm|mob|logs_ait|gerador2|tail -f /var/egsys-file/log/java/SYSAIT/PM_Generator2.log"
    "gm|mob|logs_ait|gerador3|tail -f /var/egsys-file/log/java/SYSAIT/PM_Generator3.log"
    "gm|mob|logs_ait|consumidor|tail -f /var/egsys-file/log/java/SYSAIT/PM_Consumidor.log"
    "gm|mob|logs_ait|socket_files|tail -f /var/egsys-file/log/java/SYSAIT/PM_SocketFiles.log"
    "gm|mob|logs_provider|provider|tail -f /var/egsys-file/log/java/provider/global-provider.log"
    "gm|mob|logs_email|sender|tail -f /var/egsys-file/log/java/email/email-sender.log"
    "gm|mob|logs_email|gerador|tail -f /var/egsys-file/log/java/email/email-sender-generator.log"
    # AIT Avulso
    "gm|ait|logs_ait|ait|tail -f /var/egsys-file/log/java/sysait/Logs.log"

    # --- PIAUÍ (PI) ---
    "pi|web_mob|logs_mobile|socket|tail -f /var/egsys-file/log/java/Mobile/PM_Socket.log"
    "pi|web_mob|logs_mobile|gerador|tail -f /var/egsys-file/log/java/Mobile/PM_Generator.log"
    "pi|web_mob|logs_mobile|gerador2|tail -f /var/egsys-file/log/java/Mobile/PM_Generator2.log"
    "pi|web_mob|logs_mobile|gerador3|tail -f /var/egsys-file/log/java/Mobile/PM_Generator3.log"
    "pi|web_mob|logs_mobile|consumidor|tail -f /var/egsys-file/log/java/Mobile/PM_Consumidor.log"
    "pi|web_mob|logs_mobile|socket_files|tail -f /var/egsys-file/log/java/Mobile/PM_SocketFiles.log"
    "pi|web_mob|logs_mobile|cbm_consumidor|tail -f /var/egsys-file/log/java/Mobile/CBM_Consumidor.log"
    "pi|web_mob|logs_mobile|cbm_gerador|tail -f /var/egsys-file/log/java/Mobile/CBM_Gerador.log"
    "pi|web_mob|logs_store|socket|tail -f /var/egsys-file/log/java/Store/Store_Socket.log"
    "pi|web_mob|logs_gestao|socket|tail -f /var/egsys-file/log/java/Store/Gestao_Socket.log"
    "pi|web_mob|logs_gestao|gerador|tail -f /var/egsys-file/log/java/Store/Gestao_Gerador.log"
    "pi|web_mob|logs_gestao|notificador|tail -f /var/egsys-file/log/java/Store/Gestao_Notificador.log"
    "pi|web_mob|logs_provider|provider|tail -f /var/egsys-file/log/java/Provider/GlobalProvider.log"
    "pi|web_mob|logs_email|sender|tail -f /var/egsys-file/log/java/Email/EmailSender.log"
    "pi|web_mob|logs_email|gerador|tail -f /var/egsys-file/log/java/Email/EmailSenderGenerator.log"
)

# --- FUNÇÕES DE SISTEMA ---

draw_header() {
    clear
    echo -e "${BLUE}╔══════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BLUE}║${NC}       ${BOLD}${WHITE}egSYS MONITOR - V$VERSION${NC}                                      ${BLUE}║${NC}"
    echo -e "${BLUE}╠══════════════════════════════════════════════════════════════════════╣${NC}"
    if [ ! -z "$CURRENT_USER" ]; then
        echo -e "${BLUE}║${NC} ${CYAN}User: $CURRENT_USER${NC} | ${YELLOW}$(date '+%d/%m %H:%M')${NC}                                     ${BLUE}║${NC}"
    else
        echo -e "${BLUE}║${NC} ${CYAN}SISTEMA DE LOGIN${NC}                                                 ${BLUE}║${NC}"
    fi
    echo -e "${BLUE}╚══════════════════════════════════════════════════════════════════════╝${NC}"
    echo -e "   📍 ${BOLD}$1${NC}\n"
}

spinner() {
    local pid=$1; local delay=0.1; local spinstr='|/-\'
    while [ "$(ps a | awk '{print $1}' | grep $pid)" ]; do
        local temp=${spinstr#?}; printf " [%c]  " "$spinstr"; local spinstr=$temp${spinstr%"$temp"}
        sleep $delay; printf "\b\b\b\b\b\b"
    done; printf "    \b\b\b\b"
}

log_audit() {
    local action=$1
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [USER: $CURRENT_USER] $action" >> "$AUDIT_FILE"
}

check_dependencies() {
    local missing=0
    for cmd in sshpass git ping; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${YELLOW}[AVISO] Comando '$cmd' não encontrado.${NC}"
            missing=1
        fi
    done
    if [ $missing -eq 1 ]; then
        echo -e "${RED}Por favor, rode o script 'install.sh' para corrigir dependências.${NC}"
        sleep 3
    fi
}

update_system() {
    draw_header "ATUALIZAÇÃO DE SISTEMA (GIT)"
    echo -e "   Buscando atualizações no repositório..."
    cd "$BASE_DIR" || return
    if [ -d ".git" ]; then
        git pull origin main
        if [ $? -eq 0 ]; then
            echo -e "\n   ${GREEN}✔ Sucesso! O script será reiniciado.${NC}"
            sleep 2
            exec "$0"
        else
            echo -e "\n   ${RED}✖ Erro ao atualizar.${NC}"
            read -p "Enter para voltar..."
        fi
    else
        echo -e "\n   ${RED}✖ Este diretório não é um repositório Git.${NC}"
        read -p "Enter para voltar..."
    fi
}

# --- FLUXO INICIAL ---

initial_flow() {
    draw_header "AUTENTICAÇÃO DE USUÁRIO"
    echo -ne "   👤 Digite seu nome de usuário: "
    read input_user
    if [ -z "$input_user" ]; then CURRENT_USER="Admin"; else CURRENT_USER="$input_user"; fi
    log_audit "Login efetuado"

    draw_header "CONFIGURAR LOG DE DEPURAÇÃO"
    echo -e "   1) ${GREEN}ATIVAR${NC} Log de Depuração"
    echo -e "   2) ${WHITE}SEGUIR${NC} sem ativar"
    echo ""
    echo -ne "   👉 Sua escolha: "
    read debug_opt
    if [ "$debug_opt" == "1" ]; then DEBUG_MODE=1; fi

    draw_header "CONFIGURAÇÃO DE CHAVE SSH"
    keys=($(find ~/.ssh -maxdepth 1 -type f -name "id_*" ! -name "*.pub"))
    if [ ${#keys[@]} -gt 0 ]; then
        echo -e "   Chaves encontradas em ~/.ssh:"
        i=1
        for key in "${keys[@]}"; do
            echo -e "   $i) $(basename "$key")"
            ((i++))
        done
        echo -e "   s) Pular (Usar senhas internas)"
        echo ""
        echo -ne "   👉 Selecione a chave para carregar: "
        read key_choice
        if [[ "$key_choice" =~ ^[0-9]+$ ]] && [ "$key_choice" -le "${#keys[@]}" ]; then
            key_file="${keys[$((key_choice-1))]}"
            eval "$(ssh-agent -s)" > /dev/null
            ssh-add "$key_file"
            echo -e "\n   ${GREEN}✔ Chave carregada!${NC}"
            sleep 1
        fi
    else
        echo -e "   ${YELLOW}[INFO] Nenhuma chave SSH encontrada. Usando senhas do script.${NC}"
        sleep 1
    fi
}

# --- CORE: CONEXÃO COM PARADA VIA ENTER ---

connect_ssh() {
    local client=$1; local server=$2; local log_cmd=$3; local log_name=$4
    
    local user_var="USER_${client^^}_${server^^}"; local host_var="HOST_${client^^}_${server^^}"; local pass_var="PASSWORD_${client^^}_${server^^}"
    local user=${!user_var}; local ip=${!host_var}; local senha=${!pass_var}
    
    if [ -z "$ip" ]; then echo -e "${RED}Credenciais não encontradas.${NC}"; sleep 2; return; fi
    
    draw_header "CONECTANDO..."
    echo -e "   🌎 Alvo: ${CYAN}$ip${NC}"
    echo -e "   📜 Log:  ${YELLOW}$log_name${NC}"
    
    # Ping Check
    ping -c 1 -W 2 "$ip" &> /dev/null &
    spinner $!
    if [ $? -ne 0 ]; then
        echo -e "${RED} [OFFLINE]${NC} - Servidor inacessível."
        read -p "Enter para voltar..."
        return
    else
        echo -e "${GREEN} [ONLINE]${NC}"
    fi

    echo -e "\n${WHITE}=======================================================${NC}"
    echo -e "${GREEN}   LOGS INICIADOS EM TEMPO REAL${NC}"
    echo -e "${RED}   >>> PRESSIONE [ENTER] PARA PARAR <<<${NC}"
    echo -e "${WHITE}=======================================================${NC}\n"

    # --- LÓGICA DE PARADA SEGURA ---
    # Roda o SSH em background e guarda o PID
    if command -v sshpass &> /dev/null; then
        sshpass -p "$senha" ssh -tt -o LogLevel=QUIET -o StrictHostKeyChecking=no "$user@$ip" "$log_cmd" &
    else
        ssh -tt -o LogLevel=QUIET -o StrictHostKeyChecking=no "$user@$ip" "$log_cmd" &
    fi
    SSH_PID=$!
    
    # Aguarda ENTER do usuário enquanto monitora se o processo SSH ainda vive
    while kill -0 $SSH_PID 2> /dev/null; do
        read -t 0.5 -n 1 key
        if [[ $? -eq 0 ]]; then break; fi # Se enter pressionado, sai do loop
    done

    # Mata o processo forçadamente
    kill $SSH_PID 2> /dev/null
    pkill -P $SSH_PID 2> /dev/null # Mata processos filhos
    
    echo -e "\n${YELLOW}   🛑 Conexão encerrada.${NC}"
    log_audit "Visualizou $log_name em $client-$server"
    sleep 1
}

# --- NAVEGAÇÃO ---

navigate_clients() {
    while true; do
        draw_header "MENU PRINCIPAL"
        clients=($(printf "%s\n" "${LOG_DATA[@]}" | cut -d'|' -f1 | sort | uniq))
        i=1
        for c in "${clients[@]}"; do
            count=$(printf "%s\n" "${LOG_DATA[@]}" | grep "^$c|" | wc -l)
            echo -e "   $i) ${BOLD}${CYAN}${c^^}${NC} ($count logs)"
            ((i++))
        done
        echo -e "\n   ${BLUE}──────────────────────────────────────${NC}"
        echo -e "   ${YELLOW}[U] Buscar Atualizações${NC}  ${RED}[Q] Sair${NC}"
        echo ""
        echo -ne "   👉 Opção: "
        read choice
        
        if [[ "$choice" =~ ^[qQ]$ ]]; then clear; exit 0; fi
        if [[ "$choice" =~ ^[uU]$ ]]; then update_system; continue; fi
        
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -le "${#clients[@]}" ] && [ "$choice" -gt 0 ]; then
            navigate_servers "${clients[$((choice-1))]}"
        fi
    done
}

navigate_servers() {
    local client=$1
    while true; do
        draw_header "${client^^} > SERVIDORES"
        servers=($(printf "%s\n" "${LOG_DATA[@]}" | grep "^$client|" | cut -d'|' -f2 | sort | uniq))
        i=1
        for s in "${servers[@]}"; do
            echo -e "   $i) ${MAGENTA}${s^^}${NC}"
            ((i++))
        done
        echo -e "\n   [B] Voltar"
        echo -ne "   👉 Opção: "
        read choice
        if [[ "$choice" =~ ^[bB]$ ]]; then return; fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -le "${#servers[@]}" ]; then
            navigate_logs "$client" "${servers[$((choice-1))]}"
        fi
    done
}

navigate_logs() {
    local client=$1; local server=$2
    while true; do
        draw_header "${server^^} > LOGS"
        mapfile -t log_entries < <(printf "%s\n" "${LOG_DATA[@]}" | grep "^$client|$server|")
        i=1
        for entry in "${log_entries[@]}"; do
            name=$(echo "$entry" | cut -d'|' -f4)
            cat=$(echo "$entry" | cut -d'|' -f3)
            echo -e "   $i) ${GREEN}${name^^}${NC} ${WHITE}(${cat#logs_})${NC}"
            ((i++))
        done
        echo -e "\n   [B] Voltar"
        echo -ne "   👉 Opção: "
        read choice
        if [[ "$choice" =~ ^[bB]$ ]]; then return; fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -le "${#log_entries[@]}" ]; then
            sel=${log_entries[$((choice-1))]}
            connect_ssh "$client" "$server" "$(echo "$sel" | cut -d'|' -f5)" "$(echo "$sel" | cut -d'|' -f4)"
        fi
    done
}

# --- EXECUÇÃO ---
check_dependencies
initial_flow
navigate_clients