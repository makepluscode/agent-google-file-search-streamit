#!/bin/bash

# Gemini File Search 챗봇 systemd 서비스 관리 스크립트

SERVICE_NAME="gemini-file-search"
SERVICE_FILE="/etc/systemd/system/${SERVICE_NAME}.service"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER=$(whoami)

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 도움말 출력
show_help() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}Gemini File Search 서비스 관리 도구${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
    echo "사용법:"
    echo -e "  ${GREEN}./service.sh start${NC}      - 서비스 등록, 활성화 및 시작"
    echo -e "  ${GREEN}./service.sh stop${NC}       - 서비스 중지"
    echo -e "  ${GREEN}./service.sh restart${NC}    - 서비스 재시작"
    echo -e "  ${GREEN}./service.sh status${NC}     - 서비스 상태 확인"
    echo -e "  ${GREEN}./service.sh disable${NC}    - 서비스 비활성화 및 파일 삭제"
    echo -e "  ${GREEN}./service.sh logs${NC}       - 서비스 로그 보기"
    echo ""
    echo "예시:"
    echo "  sudo ./service.sh start    # 서비스 등록 및 시작"
    echo "  sudo ./service.sh stop     # 서비스 중지"
    echo "  ./service.sh status        # 상태 확인 (sudo 불필요)"
    echo ""
}

# 서비스 파일 생성
create_service_file() {
    echo -e "${YELLOW}서비스 파일 생성 중...${NC}"

    # uv 경로 찾기 (sudo 환경에서도 작동하도록 여러 경로 확인)
    UV_PATH=""

    # SUDO_USER가 있으면 해당 사용자의 홈 디렉토리에서 찾기
    if [ -n "$SUDO_USER" ]; then
        REAL_USER_HOME=$(eval echo ~$SUDO_USER)
        if [ -f "${REAL_USER_HOME}/.local/bin/uv" ]; then
            UV_PATH="${REAL_USER_HOME}/.local/bin/uv"
        fi
    fi

    # 현재 사용자 경로에서 찾기
    if [ -z "$UV_PATH" ] && [ -f "${HOME}/.local/bin/uv" ]; then
        UV_PATH="${HOME}/.local/bin/uv"
    fi

    # PATH에서 찾기
    if [ -z "$UV_PATH" ]; then
        UV_PATH=$(which uv 2>/dev/null)
    fi

    if [ -z "$UV_PATH" ]; then
        echo -e "${RED}오류: uv가 설치되어 있지 않습니다.${NC}"
        echo "먼저 uv를 설치해주세요: curl -LsSf https://astral.sh/uv/install.sh | sh"
        echo ""
        echo "확인한 경로들:"
        echo "  - ${REAL_USER_HOME}/.local/bin/uv"
        echo "  - ${HOME}/.local/bin/uv"
        echo "  - PATH: $(echo $PATH)"
        exit 1
    fi

    echo -e "${GREEN}✓ uv 발견: ${UV_PATH}${NC}"

    # .env 파일 확인
    if [ ! -f "${SCRIPT_DIR}/.env" ]; then
        echo -e "${RED}경고: .env 파일이 없습니다.${NC}"
        echo "서비스가 시작되지 않을 수 있습니다. .env 파일을 생성해주세요."
    fi

    # systemd 서비스 파일 생성
    cat > /tmp/${SERVICE_NAME}.service << EOF
[Unit]
Description=Gemini File Search Chatbot
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${SCRIPT_DIR}
Environment="PATH=${HOME}/.local/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=${UV_PATH} run streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

    # 서비스 파일을 시스템 디렉토리로 복사
    sudo cp /tmp/${SERVICE_NAME}.service ${SERVICE_FILE}
    sudo chmod 644 ${SERVICE_FILE}
    rm /tmp/${SERVICE_NAME}.service

    echo -e "${GREEN}✓ 서비스 파일 생성 완료: ${SERVICE_FILE}${NC}"
}

# 서비스 시작
start_service() {
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}서비스 등록 및 시작${NC}"
    echo -e "${BLUE}========================================${NC}"

    # root 권한 확인
    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}오류: root 권한이 필요합니다.${NC}"
        echo "sudo ./service.sh start 로 실행해주세요."
        exit 1
    fi

    # 서비스 파일 생성
    create_service_file

    # systemd 데몬 리로드
    echo -e "${YELLOW}systemd 데몬 리로드 중...${NC}"
    sudo systemctl daemon-reload

    # 서비스 활성화
    echo -e "${YELLOW}서비스 활성화 중...${NC}"
    sudo systemctl enable ${SERVICE_NAME}

    # 서비스 시작
    echo -e "${YELLOW}서비스 시작 중...${NC}"
    sudo systemctl start ${SERVICE_NAME}

    # 상태 확인
    sleep 2
    if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}✓ 서비스가 성공적으로 시작되었습니다!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "접속 URL: http://localhost:8501"
        echo ""
        echo "유용한 명령어:"
        echo "  상태 확인: sudo systemctl status ${SERVICE_NAME}"
        echo "  로그 보기: sudo journalctl -u ${SERVICE_NAME} -f"
        echo "  서비스 중지: sudo ./service.sh stop"
    else
        echo -e "${RED}========================================${NC}"
        echo -e "${RED}✗ 서비스 시작 실패${NC}"
        echo -e "${RED}========================================${NC}"
        echo ""
        echo "로그를 확인하세요: sudo journalctl -u ${SERVICE_NAME} -n 50"
    fi
}

# 서비스 중지
stop_service() {
    echo -e "${YELLOW}서비스 중지 중...${NC}"

    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}오류: root 권한이 필요합니다.${NC}"
        echo "sudo ./service.sh stop 으로 실행해주세요."
        exit 1
    fi

    if [ ! -f "${SERVICE_FILE}" ]; then
        echo -e "${RED}오류: 서비스가 등록되어 있지 않습니다.${NC}"
        exit 1
    fi

    sudo systemctl stop ${SERVICE_NAME}
    echo -e "${GREEN}✓ 서비스가 중지되었습니다.${NC}"
}

# 서비스 재시작
restart_service() {
    echo -e "${YELLOW}서비스 재시작 중...${NC}"

    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}오류: root 권한이 필요합니다.${NC}"
        echo "sudo ./service.sh restart 로 실행해주세요."
        exit 1
    fi

    if [ ! -f "${SERVICE_FILE}" ]; then
        echo -e "${RED}오류: 서비스가 등록되어 있지 않습니다.${NC}"
        exit 1
    fi

    sudo systemctl restart ${SERVICE_NAME}
    sleep 2

    if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
        echo -e "${GREEN}✓ 서비스가 재시작되었습니다.${NC}"
    else
        echo -e "${RED}✗ 서비스 재시작 실패${NC}"
        echo "로그를 확인하세요: sudo journalctl -u ${SERVICE_NAME} -n 50"
    fi
}

# 서비스 상태 확인
status_service() {
    if [ ! -f "${SERVICE_FILE}" ]; then
        echo -e "${RED}서비스가 등록되어 있지 않습니다.${NC}"
        exit 1
    fi

    sudo systemctl status ${SERVICE_NAME}
}

# 서비스 비활성화 및 삭제
disable_service() {
    echo -e "${YELLOW}서비스 비활성화 및 삭제 중...${NC}"

    if [ "$EUID" -ne 0 ]; then
        echo -e "${RED}오류: root 권한이 필요합니다.${NC}"
        echo "sudo ./service.sh disable 로 실행해주세요."
        exit 1
    fi

    if [ ! -f "${SERVICE_FILE}" ]; then
        echo -e "${YELLOW}경고: 서비스 파일이 존재하지 않습니다.${NC}"
        exit 0
    fi

    # 서비스 중지
    if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
        echo -e "${YELLOW}서비스 중지 중...${NC}"
        sudo systemctl stop ${SERVICE_NAME}
    fi

    # 서비스 비활성화
    if sudo systemctl is-enabled --quiet ${SERVICE_NAME} 2>/dev/null; then
        echo -e "${YELLOW}서비스 비활성화 중...${NC}"
        sudo systemctl disable ${SERVICE_NAME}
    fi

    # 서비스 파일 삭제
    echo -e "${YELLOW}서비스 파일 삭제 중...${NC}"
    sudo rm -f ${SERVICE_FILE}

    # systemd 데몬 리로드
    sudo systemctl daemon-reload
    sudo systemctl reset-failed

    echo -e "${GREEN}✓ 서비스가 완전히 제거되었습니다.${NC}"
}

# 서비스 로그 보기
logs_service() {
    if [ ! -f "${SERVICE_FILE}" ]; then
        echo -e "${RED}서비스가 등록되어 있지 않습니다.${NC}"
        exit 1
    fi

    echo -e "${BLUE}로그를 표시합니다 (Ctrl+C로 종료)${NC}"
    sudo journalctl -u ${SERVICE_NAME} -f
}

# 메인 로직
case "$1" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    disable)
        disable_service
        ;;
    logs)
        logs_service
        ;;
    *)
        show_help
        exit 0
        ;;
esac

exit 0
