#!/bin/bash

echo "=========================================="
echo "🔌 開始啟動 K8s 服務 Port-Forward 轉發..."
echo "=========================================="

# 定義一個陣列，格式為 "K8s服務名稱:本地連接埠:容器連接埠"
SERVICES=(
    "asset-service:8000:8000"
    "maintenance-service:8002:8002"
    "user-service:8001:8001"
)

# 用來記錄所有背景 PID 的陣列
PIDS=()

# 監聽 Ctrl+C 訊號
trap cleanup INT

function cleanup() {
    echo -e "\n\n=========================================="
    echo "🛑 偵測到結束訊號，正在關閉所有 Port-Forward..."
    echo "=========================================="
    for pid in "${PIDS[@]}"; do
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo "➖ 已關閉 PID: $pid"
        fi
    done
    # 清理暫存的 log 檔案
    rm -f /tmp/k8s_pf_*.log
    echo "✨ 所有轉發已安全關閉，再見！"
    exit 0
}

# 依序啟動每個服務的 Port-Forward
for SVC_INFO in "${SERVICES[@]}"; do
    IFS=":" read -r SVC_NAME LOCAL_PORT CONTAINER_PORT <<< "$SVC_INFO"
    
    echo "📡 轉發服務: $SVC_NAME -> http://localhost:$LOCAL_PORT"
    
    # 💡 優化：將日誌寫入暫存檔，方便出錯時排查，不在終端機洗畫面
    LOG_FILE="/tmp/k8s_pf_${SVC_NAME}.log"
    kubectl port-forward svc/$SVC_NAME $LOCAL_PORT:$CONTAINER_PORT > "$LOG_FILE" 2>&1 &
    
    # 記錄這個背景進程的 PID
    PIDS+=($!)
    
    # 💡 優化：稍微多等一秒，確保 kubectl 順利啟動
    sleep 1
done

echo "=========================================="
echo "✅ 所有服務已在背景轉發完成！"
echo "📝 本地測試網址："
echo "   - Asset Service:       http://localhost:8000"
echo "   - Maintenance Service: http://localhost:8002"
echo "   - User Service:        http://localhost:8001"
echo "💡 提示：如果連不上，可查看 /tmp/k8s_pf_[服務名].log 檢查錯誤"
echo "🛑 欲停止轉發，請在目前視窗按下 [Ctrl + C]"
echo "=========================================="

# 讓腳本保持在前台運行
while true; do
    sleep 1
done