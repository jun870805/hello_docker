# 指定 Python 版本
FROM python:3.13-slim

# 設定工作目錄
WORKDIR /app

# 安裝 selenium
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY main.py .

# 預設執行指令
CMD ["python", "main.py"]
