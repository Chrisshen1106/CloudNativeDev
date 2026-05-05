#!/bin/bash

SERVICES=("asset:8000" "user:8001" "maintenance:8002")

echo "Start all services"

for SERVICE in "${SERVICES[@]}"; do
    IFS=":" read -r DIR PORT <<< "$SERVICE"
    
    echo "Running $DIR service on port $PORT..."
    
    # 使用 nohup 或直接在背景執行，並進入該目錄確保路徑正確
    (cd "$DIR" && uv run -m flask --app app run --port "$PORT") &
done

echo " 所有服務已在背景啟動。"
echo "若要停止所有服務，請執行: pkill -f flask"

wait