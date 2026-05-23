#!/bin/bash

# ==============================================================================
# EKS 叢集刪除腳本 (晚上關閉用)
# ==============================================================================

CLUSTER_NAME="cloud-native"
REGION="ap-east-2"

echo "=========================================="
echo "⚠️  即將開始刪除 EKS 叢集: ${CLUSTER_NAME}"
echo "📅 執行時間: $(date)"
echo "💰 刪除叢集可停止 EKS 控制平面與節點的計費"
echo "=========================================="

# 1. 刪除 Ingress 以確保 ALB 被正確清理 (選用，eksctl 刪除叢集通常也會清理)
echo "🌐 正在嘗試刪除 K8s Ingress 以清理 ALB..."
kubectl delete ingress --all --all-namespaces 2>/dev/null

# 2. 執行 eksctl 刪除指令
echo "🗑️  正在執行 eksctl delete cluster..."
eksctl delete cluster --name ${CLUSTER_NAME} --region ${REGION}

if [ $? -eq 0 ]; then
    echo "=========================================="
    echo "✅ 叢集已成功刪除！"
    echo "👋 祝你有個美好的夜晚，明天早上見！"
    echo "=========================================="
else
    echo "❌ 刪除過程中發生錯誤，請手動前往 AWS Console 檢查。"
fi
