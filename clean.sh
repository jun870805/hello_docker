#!/bin/bash
echo "🧹 正在清理所有 chrome-node 機器人..."
# 忽略錯誤訊息 (如果沒有容器時不報錯)
docker rm -f $(docker ps -aq --filter name=chrome-node) 2>/dev/null || true

echo "🛑 停止主程式..."
docker compose down

echo "✅ 清理完畢！"
