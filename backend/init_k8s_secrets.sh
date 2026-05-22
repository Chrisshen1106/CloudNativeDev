# init_k8s_secrets.sh
#!/bin/bash

# 定義設定變數
ENV_FILE=".env"
SECRET_NAME="backend-secret"

echo "=========================================="
echo "🔐 開始將本地 ${ENV_FILE} 匯入 Kubernetes Secret..."
echo "=========================================="

# 1. 檢查本地是否存在 .env 檔案
if [ ! -f "$ENV_FILE" ]; then
    echo "❌ 錯誤：找不到 ${ENV_FILE} 檔案！"
    echo "請確保你在 backend 資料夾底下，且該檔案存在。"
    exit 1
fi

# 2. 檢查目前 K8s 叢集是否已經存在同名的 Secret
# 如果存在就先刪除，避免因為重複建立而噴錯
if kubectl get secret "$SECRET_NAME" >/dev/null 2>&1; then
    echo "🔄 偵測到已存在舊的 ${SECRET_NAME}，正在進行更新（刪除舊版）..."
    kubectl delete secret "$SECRET_NAME"
fi

# 3. 從 .env 檔案自動建立 K8s Secret
echo "📥 正在讀取 ${ENV_FILE} 並建立 Kubernetes Secret [${SECRET_NAME}]..."
kubectl create secret generic "$SECRET_NAME" --from-env-file="$ENV_FILE"

# 4. 驗證建立結果
if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "✅ Secret 建立成功！"
    echo "📊 目前 [${SECRET_NAME}] 包含以下環境變數（僅顯示 Key）："
    kubectl get secret "$SECRET_NAME" -o jsonpath='{.data}' | tr ',' '\n' | cut -d'"' -f2
    echo "=========================================="
else
    echo "❌ 錯誤：建立 Secret 失敗，請檢查 K8s 連線狀態。"
    exit 1
fi