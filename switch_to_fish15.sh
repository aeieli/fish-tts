#!/bin/bash
#
# 快速切换到 Fish Speech 1.5
#

echo "🔄 切换到 Fish Speech 1.5..."
echo ""

# 停止 S1-Mini
./start_s1_mini.sh --stop 2>/dev/null

# 短暂延迟确保端口释放
sleep 2

# 启动 Fish 1.5
./start_fish15_api.sh --daemon

echo ""
echo "✅ 已切换到 Fish Speech 1.5"
echo "📍 API 地址: http://127.0.0.1:8445"
echo "📖 API 文档: http://127.0.0.1:8445/"
echo ""
