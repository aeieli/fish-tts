#!/bin/bash
#
# 快速切换到 S1-Mini
#

echo "🔄 切换到 OpenAudio S1-Mini..."
echo ""

# 停止 Fish 1.5
./start_fish15_api.sh --stop 2>/dev/null

# 短暂延迟确保端口释放
sleep 2

# 启动 S1-Mini
./start_s1_mini.sh --daemon

echo ""
echo "✅ 已切换到 S1-Mini"
echo "📍 API 地址: http://127.0.0.1:8445"
echo "📖 API 文档: http://127.0.0.1:8445/"
echo ""
