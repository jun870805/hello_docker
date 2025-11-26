import streamlit as st
import os
import time
import docker
from datetime import datetime
from selenium import webdriver

# === 設定頁面 ===
st.set_page_config(page_title="Fleet Commander", page_icon="🚀", layout="wide")

# === 初始化 ===
SCREENSHOT_DIR = "data/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs("data/downloads", exist_ok=True)
os.makedirs("data/profiles", exist_ok=True)

# 初始化 Docker Client
try:
    docker_client = docker.from_env()
except Exception as e:
    st.error(f"無法連線到 Docker Daemon: {e}")
    st.stop()

NETWORK_NAME = os.getenv("DOCKER_NETWORK", "ticket_bot")
EXTERNAL_HOST = os.getenv("EXTERNAL_HOST", "localhost")

# 初始化 Driver 記憶體
if 'drivers' not in st.session_state:
    st.session_state.drivers = {}

# === Docker 管理函數 ===

def get_active_containers():
    """找出所有由此系統產生的 Chrome 容器"""
    try:
        containers = docker_client.containers.list(filters={"label": "role=chrome-node"})
        return sorted(containers, key=lambda x: x.name)
    except:
        return []

def spawn_new_node(node_id):
    """召喚一個新的 Chrome 容器"""
    container_name = f"chrome-node-{node_id}"
    vnc_port = 7900 + int(node_id)
    
    # 掛載設定
    volume_bindings = {
        f"{os.getcwd()}/data/downloads/{container_name}": {
            'bind': '/home/seluser/Downloads', 'mode': 'rw'
        }
    }
    
    # (養號掛載預留 - 若要啟用請解開註解)
    # profile_host_path = f"{os.getcwd()}/data/profiles/{container_name}"
    # if not os.path.exists(profile_host_path): os.makedirs(profile_host_path)
    # volume_bindings[profile_host_path] = {'bind': '/chrome-profile', 'mode': 'rw'}

    try:
        try:
            existing = docker_client.containers.get(container_name)
            if existing.status == 'running':
                return True, f"{container_name} 已經在運行中"
            else:
                existing.remove(force=True)
        except docker.errors.NotFound:
            pass

        print(f"🚀 正在啟動 {container_name} (NoVNC: {vnc_port})...")
        
        docker_client.containers.run(
            image="selenium/standalone-chrome:latest",
            name=container_name,
            detach=True,
            shm_size="2g",
            network=NETWORK_NAME,
            ports={'7900/tcp': vnc_port},
            environment={
                "SE_NODE_MAX_SESSIONS": "4",
                "SE_NODE_SESSION_TIMEOUT": "60",
                "SE_VNC_NO_PASSWORD": "1",
                "TZ": "Asia/Taipei"
            },
            labels={"role": "chrome-node", "id": str(node_id)},
            security_opt=["seccomp:unconfined"],
            volumes=volume_bindings
        )
        return True, f"成功啟動 {container_name}"
    except Exception as e:
        return False, str(e)

def kill_node(container_object):
    name = container_object.name
    try:
        container_object.remove(force=True)
        # 刪除時也要清掉快取
        if name in st.session_state.drivers:
            del st.session_state.drivers[name]
        return True, f"已刪除 {name}"
    except Exception as e:
        return False, str(e)

# === Selenium 函數 ===

def get_driver(container_name):
    """
    取得指定容器的 Driver (Singleton 模式)
    如果該容器已經有連線，就重複使用；否則建立新的。
    """
    
    # 1. 檢查快取中是否已有該容器的 driver
    if container_name in st.session_state.drivers:
        existing_driver = st.session_state.drivers[container_name]
        try:
            # 🩺 心跳檢查
            _ = existing_driver.title
            return existing_driver
        except Exception:
            print(f"⚠️ [{container_name}] 連線已斷，移除快取。")
            del st.session_state.drivers[container_name]

    # 2. 建立新連線
    selenium_host = f"http://{container_name}:4444/wd/hub"
    
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    options.add_argument("--lang=zh-TW")
    options.add_argument("--disable-popup-blocking")
    
    # (養號參數預留)
    # options.add_argument("--user-data-dir=/chrome-profile")

    print(f"🔵 [{container_name}] 建立新連線...")
    driver = webdriver.Remote(command_executor=selenium_host, options=options)
    
    # 自動導向 Google (避免空白頁)
    if driver.current_url == 'data:,':
        driver.get("https://www.google.com")

    # 存入快取
    st.session_state.drivers[container_name] = driver
    return driver

def navigate_to(container_name, url):
    try:
        driver = get_driver(container_name)
        driver.get(url)
        return True, f"[{container_name}] 成功前往"
    except Exception as e:
        return False, str(e)

def take_screenshot(container_name):
    try:
        driver = get_driver(container_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{SCREENSHOT_DIR}/{container_name}_{timestamp}.png"
        driver.save_screenshot(filename)
        return True, filename
    except:
        return False, None

# === UI 介面 ===

st.title("🚀 艦隊指揮官 (Dynamic Fleet)")

# --- 側邊欄：艦隊管理 ---
with st.sidebar:
    st.header("🏗️ 艦隊管理")
    
    # 🔥🔥🔥 自動 ID 生成邏輯 🔥🔥🔥
    if st.button("➕ 召喚新機器人", type="primary", use_container_width=True):
        # 1. 掃描目前有的容器
        current_containers = get_active_containers()
        existing_ids = []
        for c in current_containers:
            # 優先嘗試讀取 label
            lid = c.labels.get('id')
            if lid and lid.isdigit():
                existing_ids.append(int(lid))
            else:
                # 如果沒有 label，嘗試解析名稱 chrome-node-1
                try:
                    parts = c.name.split('-')
                    if parts[-1].isdigit():
                        existing_ids.append(int(parts[-1]))
                except:
                    pass
        
        # 2. 計算下一個 ID (最大值 + 1)
        new_id = max(existing_ids) + 1 if existing_ids else 1
        
        # 3. 執行召喚
        with st.spinner(f"正在召喚 Node-{new_id}..."):
            ok, msg = spawn_new_node(new_id)
            if ok:
                st.success(f"Node-{new_id} 就緒！")
                time.sleep(1)
                st.rerun()
            else:
                st.error(f"失敗: {msg}")

    st.divider()
    
    active_containers = get_active_containers()
    node_names = [c.name for c in active_containers]
    
    selected_node = None
    if not node_names:
        st.warning("目前沒有活躍的機器人")
    else:
        selected_node = st.selectbox("🎮 選擇操作目標", node_names)
        
        if selected_node:
            current_container = next((c for c in active_containers if c.name == selected_node), None)
            if current_container:
                try:
                    ports = current_container.attrs['NetworkSettings']['Ports']
                    vnc_data = ports.get('7900/tcp')
                    if vnc_data:
                        vnc_port = vnc_data[0]['HostPort']
                        st.info(f"**NoVNC:** http://{EXTERNAL_HOST}:{vnc_port}")
                    else:
                        st.warning("NoVNC Port 未對應")
                except:
                    st.warning("無法讀取 Port 資訊")
                
                col_k1, col_k2 = st.columns(2)
                if col_k1.button(f"💀 銷毀", type="secondary", use_container_width=True):
                    ok, msg = kill_node(current_container)
                    if ok:
                        st.success(msg)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(msg)
                
                if col_k2.button("🔄 重置連線", use_container_width=True):
                    if selected_node in st.session_state.drivers:
                        try:
                            st.session_state.drivers[selected_node].quit()
                        except:
                            pass
                        del st.session_state.drivers[selected_node]
                    st.success("連線已重置")

# --- 主畫面 ---
if selected_node:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader(f"🕹️ 控制: {selected_node}")
        url_input = st.text_input("目標網址", value="https://www.google.com", key="url")
        
        c1, c2 = st.columns(2)
        if c1.button("🚀 前往網頁", use_container_width=True):
            with st.spinner("執行中..."):
                ok, msg = navigate_to(selected_node, url_input)
                if ok:
                    st.success(msg)
                    res, path = take_screenshot(selected_node)
                    if res:
                        st.session_state['last_shot'] = path
                else:
                    st.error(msg)
        
        if c2.button("📸 截圖", use_container_width=True):
            res, path = take_screenshot(selected_node)
            if res:
                st.success("截圖成功")
                st.session_state['last_shot'] = path
            else:
                st.error("截圖失敗")

    with col2:
        st.subheader("畫面預覽")
        if 'last_shot' in st.session_state and st.session_state.get('last_shot'):
            st.image(st.session_state['last_shot'])
        else:
            st.info("尚無畫面")

else:
    st.info("👈 請先在側邊欄新增或選擇一個機器人")

st.divider()
if os.path.exists(SCREENSHOT_DIR):
    files = sorted(os.listdir(SCREENSHOT_DIR), reverse=True)[:6]
    st.caption("最近截圖:")
    cols = st.columns(6)
    for idx, f in enumerate(files):
        with cols[idx % 6]:
            st.image(f"{SCREENSHOT_DIR}/{f}", caption=f.split("_")[0])
