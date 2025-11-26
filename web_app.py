import streamlit as st
import os
import time
from datetime import datetime
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, InvalidSessionIdException

# === 設定頁面 ===
st.set_page_config(page_title="Docker Bot Control", page_icon="🎮", layout="wide")

# === 初始化截圖目錄 ===
SCREENSHOT_DIR = "data/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# === 核心函數 ===

def get_driver():
    """
    智慧型取得 Driver：自動偵測連線是否存活，若斷線則自動重連 (Self-Healing)
    """
    # 1. 嘗試取得快取中的 driver
    driver = _get_cached_driver()
    
    try:
        # 2. 健康檢查 (Heartbeat Check)
        # 嘗試讀取當前的 URL，如果 Session 死了，這裡會立刻報錯
        _ = driver.current_url
        return driver
        
    except Exception as e:
        print(f"⚠️ 偵測到瀏覽器連線中斷 ({e})，正在自動重連...")
        
        # 3. 清除死掉的快取
        st.cache_resource.clear()
        
        # 4. 重新建立一個新的連線
        return _get_cached_driver()

@st.cache_resource(show_spinner=False)
def _get_cached_driver():
    selenium_host = os.getenv('SELENIUM_HOST', 'http://chrome:4444/wd/hub')
    
    options = webdriver.ChromeOptions()
    
    # 1. 防止 Docker 崩潰
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    # 2. 養號設定
    # options.add_argument("--user-data-dir=/chrome-profile")
    
    # 3. 偽裝
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    print("🔵 正在建立新的 Chrome 連線...")
    driver = webdriver.Remote(command_executor=selenium_host, options=options)
    return driver

def navigate_to(url):
    try:
        driver = get_driver()
        driver.get(url)
        return True, "成功前往"
    except Exception as e:
        # 如果連線斷了，清除快取讓下次重連
        st.cache_resource.clear()
        return False, str(e)

def take_screenshot():
    try:
        driver = get_driver()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{SCREENSHOT_DIR}/snap_{timestamp}.png"
        driver.save_screenshot(filename)
        return True, filename
    except:
        return False, None

# === UI 介面 ===

st.title("🎮 Docker 瀏覽器中控台")

with st.sidebar:
    st.header("操作面板")
    url_input = st.text_input("輸入網址", value="https://www.google.com")
    
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        go_btn = st.button("🚀 前往網頁", type="primary")
    with col_btn2:
        snap_btn = st.button("📸 截圖")
        
    st.divider()
    
    if st.button("🛑 重置連線 (Reset)"):
        # 這個版本只清除快取，沒有去關閉舊的 Driver
        st.cache_resource.clear()
        st.warning("已清除驅動快取，下次操作將開啟新視窗。")

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("瀏覽器畫面")
    image_placeholder = st.empty()
    
    if go_btn:
        with st.spinner(f"正在前往 {url_input}..."):
            success, msg = navigate_to(url_input)
            if success:
                st.success(f"✅ {msg}")
                ok, path = take_screenshot()
                if ok:
                    image_placeholder.image(path)
            else:
                st.error(f"❌ 錯誤: {msg}")

    elif snap_btn:
        ok, path = take_screenshot()
        if ok:
            st.success("✅ 截圖成功")
            image_placeholder.image(path)
        else:
            st.error("❌ 截圖失敗")

with col2:
    st.subheader("ℹ️ 狀態資訊")
    
    host_name = os.getenv('EXTERNAL_HOST', 'localhost')
    st.info(f"NoVNC 入口：\nhttp://{host_name}:7900")
    
    try:
        # 這裡直接拿快取來顯示，不觸發重連
        if _get_cached_driver.check_invariant():
             driver = _get_cached_driver()
             st.write(f"**標題:** {driver.title}")
             st.write(f"**網址:** {driver.current_url}")
        else:
             st.write("⚪ 瀏覽器未連線")
    except:
        st.write("🔴 連線可能已中斷")

st.divider()
with st.expander("📂 歷史截圖"):
    if os.path.exists(SCREENSHOT_DIR):
        files = sorted(os.listdir(SCREENSHOT_DIR), reverse=True)[:5]
        cols = st.columns(len(files)) if files else []
        for idx, f in enumerate(files):
            with cols[idx]:
                st.image(f"{SCREENSHOT_DIR}/{f}", caption=f)
