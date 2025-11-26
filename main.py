import time
import os
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 隱藏 WebDriver 特徵的 JS
STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
Object.defineProperty(navigator, 'languages', { get: () => ['zh-TW', 'zh', 'en-US'] });
"""

def run_health_check():
    print("🔵 [1/6] 正在連線到 Docker Chrome...")
    
    options = webdriver.ChromeOptions()
    # 模擬真實瀏覽器 User-Agent (Linux Desktop)
    options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
   
    # 這樣 Chrome 就會把 Cookies 和登入資訊寫入我們掛載的那個資料夾
    options.add_argument("--user-data-dir=/chrome-profile")

    # === 🔥 必加！防止 Docker 內 Chrome 崩潰的救命參數 ===
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # ===================================================

    # 讓 Chrome 啟動時不要跳出 "Chrome 正在受到自動測試軟體控制"
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # 🔥 加入這行最強力的偽裝參數
    options.add_argument("--disable-blink-features=AutomationControlled")

    selenium_host = os.getenv('SELENIUM_HOST', 'http://chrome:4444/wd/hub')
    
    driver = None
    # 重試機制
    for i in range(15):
        try:
            driver = webdriver.Remote(command_executor=selenium_host, options=options)
            break
        except:
            print(f"   連線重試中 ({i+1}/15)...")
            time.sleep(2)
    
    if not driver:
        print("❌ 連線失敗：Chrome 未啟動")
        return

    # ★ 注入隱身腳本
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": STEALTH_JS})
    
    print("🟢 連線成功！開始全系統健檢...")

    try:
        # === 測試 1: 時區 ===
        print("\n🕐 [2/6] 檢查時區 (Timezone)...")
        browser_time = driver.execute_script("return new Date().toString()")
        print(f"   🌏 Chrome 時間: {browser_time}")
        if "Taipei" in browser_time or "GMT+08" in browser_time:
            print("   ✅ 時區正確 (Asia/Taipei)")
        else:
            print("   ⚠️ 警告：時區錯誤！搶票會遲到！")

        # === 測試 2: 爬蟲特徵 ===
        print("\n🕵️ [3/6] 檢查爬蟲特徵 (Bot Detection)...")
        driver.get("https://bot.sannysoft.com/")
        time.sleep(2)
        webdriver_flag = driver.execute_script("return navigator.webdriver")
        print(f"   👀 navigator.webdriver = {webdriver_flag}")
        if not webdriver_flag:
            print("   ✅ 隱身成功")
        else:
            print("   ❌ 失敗：被偵測為機器人")

        # === 測試 3: 中文顯示 ===
        print("\n🀄 [4/6] 檢查中文字型...")
        driver.get("https://www.google.com.tw")
        search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.NAME, "q")))
        search_box.send_keys("拓元售票") # 輸入中文
        print("   ✅ 已輸入中文，請稍後檢查畫面是否顯示亂碼")

        # === 測試 4: 登入狀態 (養號) ===
        print("\n👤 [5/6] 檢查 Google 登入狀態...")
        # 檢查右上角是否有 "Sign in" 按鈕，如果有代表沒登入
        page_source = driver.page_source
        if "登入" in page_source or "Sign in" in page_source:
             print("   ⚠️  狀態：未登入 (請手動登入以解決 reCAPTCHA)")
        else:
             print("   ✅ 狀態：疑似已登入 (找不到登入按鈕)")

        # === 測試 5: 截圖存證 ===
        print("\n📸 [6/6] 儲存截圖...")
        driver.save_screenshot("./data/health_check.png")
        print("   已儲存: health_check.png")

        print("\n✨ 測試結束！")
        print("🚨 請現在打開瀏覽器 (http://ticket-bot:7900) 進行手動登入！")
        print("⏳ 程式將掛機 600 秒 (10分鐘) 讓你操作...")
        
        time.sleep(600)

    except Exception as e:
        print(f"❌ 發生錯誤: {e}")
    finally:
        try:
            driver.quit()
            print("👋 瀏覽器已關閉")
        except:
            pass

if __name__ == "__main__":
    run_health_check()
