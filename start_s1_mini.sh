#!/bin/bash
#
# OpenAudio S1-Mini API Server 启动脚本
# 使用正确的 modded_dac_vq 配置和 codec.pth
#
# 使用方法:
#   ./start_s1_mini.sh              # 前台运行
#   ./start_s1_mini.sh --daemon     # 后台运行
#   ./start_s1_mini.sh --stop       # 停止后台服务
#

set -e

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="${SCRIPT_DIR}/fishenv"
PID_FILE="${SCRIPT_DIR}/s1_mini.pid"
LOG_FILE="${SCRIPT_DIR}/s1_mini.log"

# S1-Mini 模型路径（使用正确的配置）
LLAMA_CHECKPOINT="${LLAMA_CHECKPOINT:-checkpoints/openaudio-s1-mini}"
DECODER_CHECKPOINT="${DECODER_CHECKPOINT:-checkpoints/openaudio-s1-mini/codec.pth}"
DECODER_CONFIG="${DECODER_CONFIG:-modded_dac_vq}"

# 服务器配置
HOST="${API_HOST:-0.0.0.0}"
PORT="${API_PORT:-8445}"  # 使用相同端口（与Fish 1.5互斥运行）
DEVICE="${API_DEVICE:-cuda}"
WORKERS="${API_WORKERS:-1}"
MODE="${API_MODE:-tts}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查虚拟环境
check_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        print_error "虚拟环境不存在: $VENV_DIR"
        exit 1
    fi
}

# 激活虚拟环境
activate_venv() {
    print_info "激活虚拟环境..."
    source "${VENV_DIR}/bin/activate"
}

# 检查模型文件
check_model() {
    print_info "检查模型文件..."

    if [ ! -d "$LLAMA_CHECKPOINT" ]; then
        print_error "S1-Mini 模型不存在: $LLAMA_CHECKPOINT"
        exit 1
    fi

    local model_file="${LLAMA_CHECKPOINT}/model.pth"
    if [ ! -f "$model_file" ]; then
        print_error "模型文件不存在: $model_file"
        exit 1
    fi

    if [ ! -f "$DECODER_CHECKPOINT" ]; then
        print_error "Codec 文件不存在: $DECODER_CHECKPOINT"
        print_info "S1-Mini 需要使用 codec.pth，不是 firefly-gan-vq"
        exit 1
    fi

    print_success "模型文件检查通过"
}

# 启动服务（前台）
start_foreground() {
    print_info "启动 OpenAudio S1-Mini API 服务器..."
    echo ""
    print_info "配置信息:"
    print_info "  模型: OpenAudio S1-Mini (10 codebooks)"
    print_info "  模型路径: ${LLAMA_CHECKPOINT}"
    print_info "  Codec: ${DECODER_CHECKPOINT}"
    print_info "  Decoder配置: ${DECODER_CONFIG}"
    print_info "  设备: ${DEVICE}"
    print_info "  监听地址: http://${HOST}:${PORT}"
    print_info "  工作进程: ${WORKERS}"
    echo ""
    print_info "API 文档: http://${HOST}:${PORT}/"
    echo ""

    cd "$SCRIPT_DIR"

    # 构建命令（使用正确的配置）
    local cmd="python tools/api_server.py \
        --mode ${MODE} \
        --llama-checkpoint-path ${LLAMA_CHECKPOINT} \
        --decoder-checkpoint-path ${DECODER_CHECKPOINT} \
        --decoder-config-name ${DECODER_CONFIG} \
        --device ${DEVICE} \
        --listen ${HOST}:${PORT} \
        --workers ${WORKERS}"

    # 可选参数
    if [ "${API_HALF}" = "true" ]; then
        cmd="${cmd} --half"
        print_info "  使用半精度 (FP16)"
    fi

    if [ "${API_COMPILE}" = "true" ]; then
        cmd="${cmd} --compile"
        print_info "  启用编译加速"
    fi

    if [ -n "${API_KEY}" ]; then
        cmd="${cmd} --api-key ${API_KEY}"
        print_info "  已启用 API Key 认证"
    fi

    echo ""
    print_info "执行命令: $cmd"
    echo ""

    # 执行命令
    eval $cmd
}

# 启动服务（后台）
start_daemon() {
    if [ -f "$PID_FILE" ]; then
        local old_pid=$(cat "$PID_FILE")
        if kill -0 "$old_pid" 2>/dev/null; then
            print_warning "S1-Mini 服务已在运行 (PID: ${old_pid})"
            print_info "如需重启，请先运行: $0 --stop"
            exit 1
        else
            print_warning "发现旧的 PID 文件，清理中..."
            rm -f "$PID_FILE"
        fi
    fi

    print_info "启动 OpenAudio S1-Mini API 服务器（后台模式）..."
    echo ""
    print_info "配置信息:"
    print_info "  模型: OpenAudio S1-Mini (10 codebooks)"
    print_info "  Codec: codec.pth (DAC架构)"
    print_info "  设备: ${DEVICE}"
    print_info "  监听地址: http://${HOST}:${PORT}"
    print_info "  日志文件: ${LOG_FILE}"
    echo ""

    cd "$SCRIPT_DIR"

    local cmd="python tools/api_server.py \
        --mode ${MODE} \
        --llama-checkpoint-path ${LLAMA_CHECKPOINT} \
        --decoder-checkpoint-path ${DECODER_CHECKPOINT} \
        --decoder-config-name ${DECODER_CONFIG} \
        --device ${DEVICE} \
        --listen ${HOST}:${PORT} \
        --workers ${WORKERS}"

    if [ "${API_HALF}" = "true" ]; then
        cmd="${cmd} --half"
    fi

    if [ "${API_COMPILE}" = "true" ]; then
        cmd="${cmd} --compile"
    fi

    if [ -n "${API_KEY}" ]; then
        cmd="${cmd} --api-key ${API_KEY}"
    fi

    nohup bash -c "source ${VENV_DIR}/bin/activate && $cmd" > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo "$pid" > "$PID_FILE"

    print_info "等待服务启动..."
    sleep 8

    if kill -0 "$pid" 2>/dev/null; then
        print_success "S1-Mini 服务启动成功 (PID: ${pid})"
        print_info "API 地址: http://${HOST}:${PORT}"
        print_info "API 文档: http://${HOST}:${PORT}/"
        print_info "查看日志: tail -f ${LOG_FILE}"
        print_info "停止服务: $0 --stop"
    else
        print_error "服务启动失败，请查看日志: ${LOG_FILE}"
        tail -50 "$LOG_FILE"
        exit 1
    fi
}

# 停止服务
stop_daemon() {
    if [ ! -f "$PID_FILE" ]; then
        print_warning "未找到 PID 文件，服务可能未运行"
        exit 1
    fi

    local pid=$(cat "$PID_FILE")
    print_info "停止 S1-Mini 服务 (PID: ${pid})..."

    if kill -0 "$pid" 2>/dev/null; then
        kill "$pid"
        local count=0
        while kill -0 "$pid" 2>/dev/null && [ $count -lt 10 ]; do
            sleep 1
            count=$((count + 1))
        done

        if kill -0 "$pid" 2>/dev/null; then
            print_warning "进程未响应，强制终止..."
            kill -9 "$pid"
        fi

        rm -f "$PID_FILE"
        print_success "服务已停止"
    else
        print_warning "进程不存在 (PID: ${pid})"
        rm -f "$PID_FILE"
    fi
}

# 查看状态
show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            print_success "S1-Mini 服务正在运行 (PID: ${pid})"
            print_info "API 地址: http://${HOST}:${PORT}"
            print_info "日志文件: ${LOG_FILE}"
        else
            print_warning "PID 文件存在但进程未运行"
        fi
    else
        print_info "S1-Mini 服务未运行"
    fi
}

# 显示帮助
show_help() {
    cat << EOF
OpenAudio S1-Mini API Server 启动脚本

使用方法:
  $0 [选项]

选项:
  (无)           前台运行服务器
  --daemon, -d   后台运行服务器
  --stop, -s     停止后台服务器
  --status       查看服务状态
  --help, -h     显示此帮助信息

环境变量:
  API_HOST       监听地址（默认: 0.0.0.0）
  API_PORT       监听端口（默认: 8446）
  API_DEVICE     设备（默认: cuda）
  API_HALF       使用半精度（true/false）
  API_COMPILE    编译加速（true/false）

示例:
  # 前台运行
  $0

  # 后台运行
  $0 --daemon

  # 使用半精度 + 编译加速
  API_HALF=true API_COMPILE=true $0 --daemon

EOF
}

# 主函数
main() {
    cd "$SCRIPT_DIR"

    local mode="foreground"
    while [[ $# -gt 0 ]]; do
        case $1 in
            --daemon|-d)
                mode="daemon"
                shift
                ;;
            --stop|-s)
                mode="stop"
                shift
                ;;
            --status)
                mode="status"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                print_error "未知选项: $1"
                show_help
                exit 1
                ;;
        esac
    done

    echo ""
    echo "=========================================="
    echo "  OpenAudio S1-Mini API Server"
    echo "  完整 10-codebook DAC 支持"
    echo "=========================================="
    echo ""

    if [ "$mode" = "stop" ]; then
        stop_daemon
        exit 0
    elif [ "$mode" = "status" ]; then
        show_status
        exit 0
    fi

    check_venv
    activate_venv
    check_model

    if [ "$mode" = "daemon" ]; then
        start_daemon
    else
        start_foreground
    fi
}

main "$@"
