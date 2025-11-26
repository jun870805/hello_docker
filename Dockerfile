FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV TZ=Asia/Taipei

# 安裝系統依賴 + 中文字型 (修正版 libgl1)
RUN apt-get update && apt-get install -y \
    git curl libgl1 libglib2.0-0 \
    fonts-noto-cjk fonts-wqy-zenhei \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["streamlit", "run", "web_app.py"]
