#!/bin/bash

# 設定顏色變數 (讓輸出比較漂亮)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🧹 [1/4] 正在清理舊戰場...${NC}"

# 1. 獵殺所有動態產生的 Chrome 節點 (解決 Network 佔用問題)
# 使用 2>/dev/null 隱藏「找不到容器」的錯誤訊息，讓畫面乾淨
docker rm -f $(docker ps -aq --filter name=chrome-node) 2>/dev/null || true

# 2. 停止並移除中控台容器
docker compose down --remove-orphans 2>/dev/null

echo -e "${GREEN}   ✅ 舊容器與殘留網路已清除${NC}"


echo -e "${YELLOW}🔧 [2/4] 初始化資料夾與權限...${NC}"

# 3. 確保資料夾存在
mkdir -p data/downloads
mkdir -p data/screenshots
mkdir -p data/profiles

# 4. 設定權限 (給 Docker 內部的 seluser 使用，UID 1200)
# 這裡需要 sudo，執行時可能會問你密碼
sudo chown -R 1200:1200 data
sudo chmod -R 777 data

echo -e "${GREEN}   ✅ 資料夾權限設定完成 (UID 1200)${NC}"


echo -e "${YELLOW}🚀 [3/4] 正在建置並啟動系統...${NC}"

# 5. 啟動 Docker Compose
docker compose up -d --build


echo -e "${GREEN}🎉 [4/4] 系統啟動成功！${NC}"

# 6. 抓取本機 IP 提示使用者
HOST_IP=$(hostname -I | awk '{print $1}')

echo "======================================================"
echo -e "   👉 中控台網址: ${GREEN}http://${HOST_IP}:8501${NC}"
echo -e "   👉 或是:       ${GREEN}http://peterfan0805:8501${NC}"
echo "======================================================"
echo -e "💡 若要查看 Log，請輸入: ${YELLOW}docker compose logs -f bot${NC}"
