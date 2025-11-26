#!/bin/bash

echo "🚀 初始化專案資料夾與權限..."

# 1. 建立資料夾結構
mkdir -p data/profile
mkdir -p data/downloads
mkdir -p data/screenshots

# 2. 設定權限 (給 Docker 內部的 seluser 使用)
# 1200 是 selenium/standalone-chrome 映像檔預設的 UID
echo "🔧 設定權限為 UID 1200..."
sudo chown -R 1200:1200 data
sudo chmod -R 777 data

echo "✅ 初始化完成！你可以執行 'docker compose up -d' 了。"
