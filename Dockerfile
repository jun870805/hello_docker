# 使用 Python 3.13 輕量版
FROM python:3.13-slim

# 設定環境變數：不產生 pyc 檔、Log 立即輸出
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# 設定時區為台北 (確保 Python 程式時間正確)
ENV TZ=Asia/Taipei

# 安裝系統依賴 + 中文字型 (fonts-noto-cjk)
# libgl1/libglib2.0 是為了未來跑 OCR 預先準備的
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libgl1 \
    libglib2.0-0 \
    fonts-noto-cjk \
    fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

# 設定工作目錄
WORKDIR /app

# 安裝套件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 預設指令
CMD ["python", "main.py"]
