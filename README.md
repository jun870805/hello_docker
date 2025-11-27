# **🚀 Auto Task Fleet Commander (自動化任務艦隊中控台)**

&emsp;&emsp;這是一個基於 Docker 與 Streamlit 的自動化網頁控制系統，專為高負載自動化任務設計。  

&emsp;&emsp;採用 Docker-out-of-Docker (DooD) 架構，允許透過網頁介面動態「召喚」多個獨立的 Chrome 容器，並組成艦隊進行平行任務。

## **✨ 特色功能**

* **艦隊化管理 (Fleet Management)**：
  
  * 透過 Web 介面一鍵新增/銷毀 Chrome 機器人。
    
  * 支援多工平行運作，每個機器人獨立運作，互不干擾。
    
* **強大的偽裝能力 (Stealth)**：
  
  * 內建防偵測參數 (AutomationControlled 移除)。
    
  * 模擬真實使用者行為，有效繞過 Google reCAPTCHA 與 Cloudflare。
    
* **自動癒合 (Self-Healing)**：
  
  * Selenium 連線斷開時自動偵測並修復。
    
  * 手動關閉視窗後，程式會自動重啟新視窗，不會崩潰。
    
* **NoVNC 即時監控**：
  
  * 每個機器人都有獨立的桌面視窗 (Port 7901, 7902...)。
    
  * 可隨時介入操作 (如手動輸入信用卡號、OTP)。
    
* **防崩潰機制**：
  
  * 針對 Linux Docker 環境 (Kernel 6.8+) 優化。
    
  * 解決 session not created 與記憶體不足問題 (shm\_size=2g, seccomp:unconfined)。
    
* **一鍵部署**：
  
  * 提供 start.sh 自動化腳本，自動處理權限、清理殘留容器與網路。

## **🛠️ 系統架構**

* **中控台 (Manager)**: 運行 Streamlit 的容器，掛載了宿主機的 docker.sock，擁有控制 Docker 的權限。
  
* **節點 (Nodes)**: 動態生成的 selenium/standalone-chrome 容器 (Sibling Containers)。
  
* **網路 (Network)**: 所有容器皆加入專屬的 ticket\_bot 橋接網路，確保互通。

## **📂 目錄結構**

```
.  
├── start.sh                 # 一鍵啟動腳本 (包含權限修復與清理)  
├── docker-compose.yml       # 定義中控台服務與網路架構  
├── Dockerfile               # 定義中控台環境 (Python 3.13 \+ 中文字型)  
├── web_app.py               # 核心程式碼 (Streamlit 介面與邏輯)
├── requirements.txt         # Python 相依套件  
└── data/                    # 資料掛載區 (由腳本自動建立)  
    ├── downloads/           # 各節點的下載檔案 (依容器名稱分類)  
    ├── screenshots/         # 自動截圖存檔  
    └── profiles/            # (選用) 瀏覽器設定檔，用於養號
```

## **🚀 快速開始 (Quick Start)**

### **1\. 啟動系統**

&emsp;&emsp;無需手動輸入複雜的 docker 指令，直接執行啟動腳本：

&emsp;&emsp; ``` chmod \+x start.sh  && ./start.sh ```

&emsp;&emsp;腳本會自動執行以下動作：

&emsp;&emsp;1. **清理戰場**：移除殘留的 chrome-node 容器 (避免 Network is in use 錯誤)。  
&emsp;&emsp;2. **權限修復**：建立 data/ 資料夾並設定權限為 UID 1200 (給 Chrome 使用)。  
&emsp;&emsp;3. **啟動服務**：建置並啟動 Docker Compose。

### **2\. 存取中控台**

&emsp;&emsp;啟動成功後，請在瀏覽器輸入： ```http://{Server IP}:8501```

### **3\. 召喚機器人**

&emsp;&emsp;1. 在側邊欄「新增節點 ID」輸入 1 (或其他數字)，點擊 **\[➕ 召喚新機器人\]**。  
&emsp;&emsp;2. 等待約 3 秒，下拉選單選擇 **chrome-node-1**。  
&emsp;&emsp;3. 輸入網址並點擊 **\[🚀 前往網頁\]**。

### **4\. 監控與接管 (NoVNC)**

&emsp;&emsp;網頁會顯示該節點的 NoVNC 連結（預設無密碼）：

&emsp;&emsp;Node 1: ```http://{Server IP}:7901```

&emsp;&emsp;Node 2: http://{Server IP}:7902  

&emsp;&emsp;Node N: http://{Server IP}:7900+N

## **⚙️ 進階設定說明**

### **關於養號 (Google 登入保持)**

&emsp;&emsp;目前程式碼預設為 **無痕模式 (Clean Session)**，適合高強度測試。若需要保留 Google 登入狀態以降低驗證碼機率：

&emsp;&emsp;1. 修改 web\_app.py 中的 get\_driver 函式，解開以下註解：

&emsp;&emsp;&emsp;&emsp;``` # options.add_argument("--user-data-dir=/chrome-profile") ```

&emsp;&emsp;2. 修改 web\_app.py 中的 spawn\_new\_node 函式，解開 volumes 掛載 profiles 的註解。
   
&emsp;&emsp;3. 重啟系統。

### **關於安全限制 (核彈級解法)**

&emsp;&emsp;為了防止 Chrome 在新版 Linux Kernel (6.8+) 崩潰，我們在動態生成容器時使用了：

&emsp;&emsp;security\_opt=\["seccomp:unconfined"\]

&emsp;&emsp;這會解除 Docker 的系統呼叫限制，確保 Chrome 穩定運行，但也降低了容器的隔離性 (在內網環境下可接受)。

## **🐛 常見問題排除**

**Q: 啟動時出現 Network ticket\_bot is in use？**

**A:** 這是因為有「私生子容器」還沒刪除。請直接執行 ./start.sh，它會自動獵殺殘留容器。

**Q: Chrome 啟動後立刻崩潰 (Exited)？**

**A:** 通常是權限問題。請確認 data/ 資料夾擁有者是否為 UID 1200。執行 ./start.sh 會自動修復此問題。

**Q: 網頁卡在「正在前往...」很久？**

**A:** 可能是舊的 Session 卡死。請點擊側邊欄的 **\[🛑 重置連線\]** 按鈕，或是手動去 NoVNC 關閉瀏覽器視窗。

**Q: 如何在 Mac 上查看截圖？**

**A:** 截圖會存在 Linux 的 data/screenshots。你可以透過 scp 下載，或是直接在中控台網頁下方查看預覽。



*Project developed by Peter Fan.*
