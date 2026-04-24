# CloudNativeDev
台大雲原生第十組

frontend使用方法_Rapid
1. 在自己terminal cd dekstop
2. git clone repo_name
3. 打開檔案 cd frontend
4. npm install
5. npm run dev


# 先進入asset-service的微服務資料夾
cd backend\asset-service

(第一次 pip install -r requirments.txt)

# 啟動虛擬環境 (這是 Windows PowerShell 專用的指令)
.\venv\Scripts\Activate

# 開啟後端服務
python app.py

# swagger UI
http://127.0.0.1:5000/apidocs/