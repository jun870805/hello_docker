import time
import os
from selenium import webdriver
# 記得 import 這個例外處理
from urllib3.exceptions import MaxRetryError 

def run_demo():
    print("🔵 正在連線到遠端 Docker Chrome...")
    
    options = webdriver.ChromeOptions()
    
    # 讀取環境變數
    selenium_host = os.getenv('SELENIUM_HOST', 'http://chrome:4444/wd/hub')
    
    driver = None
    
    # === 關鍵修改：重試迴圈 ===
    print(f"   目標位址: {selenium_host}")
    for i in range(30): # 嘗試 30 次 (約 60秒)
        try:
            print(f"   嘗試連線第 {i+1} 次...")
            driver = webdriver.Remote(
                command_executor=selenium_host,
                options=options
            )
            break # 連線成功，跳出迴圈
        except Exception as e:
            print(f"   ⚠️ 連線失敗，等待 2 秒後重試...")
            time.sleep(2)
            
    if driver is None:
        print("❌ 錯誤：無法連線到 Chrome，程式結束。")
        return
    # ========================

    print("🟢 連線成功！正在顯示 Hello World...")

    # ... (後面顯示 HTML 的程式碼不用改，照舊) ...
    html_content = """
    data:text/html;charset=utf-8,
    <div style='display:flex;justify-content:center;align-items:center;height:100vh;background-color:#f0f0f0;flex-direction:column;'>
        <h1 style='color:#ff6b6b;font-size:50px;'>Hello World!</h1>
        <h2 style='color:#333;'>這是你在 Docker 裡的 Chrome</h2>
        <p>請嘗試用滑鼠選取這段文字，證明你可以控制它！</p>
    </div>
    """
    driver.get(html_content)

    print("✨ 畫面已產生！請立刻切換到瀏覽器觀看 http://ticket-bot:7900")
    print("⏳ 程式將暫停 300 秒讓你玩耍...")
    
    time.sleep(300)
    driver.quit()
    print("👋 測試結束。")

if __name__ == "__main__":
    run_demo()
