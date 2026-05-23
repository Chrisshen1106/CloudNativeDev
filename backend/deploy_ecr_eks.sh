# deploy_ecr_eks.sh
#!/bin/bash

# ==============================================================================
# 1. 定義變數
# ==============================================================================
AWS_ACCOUNT_ID="794934876006"
AWS_REGION="ap-east-2"
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

# 取得當前時間作為唯一版本號（格式：20260519-012530）
VERSION=$(date +%Y%m%d-%H%M%S)

echo "=========================================="
echo "🚀 開始執行 ECR 打包與 EKS 自動部署腳本"
echo "📅 目前版本號 (TAG): ${VERSION}"
echo "=========================================="

# ==============================================================================
# 2. 登入 AWS ECR
# ==============================================================================
echo "🔑 正在登入 Amazon ECR..."
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REGISTRY}

if [ $? -ne 0 ]; then
    echo "❌ ECR 登入失敗，請檢查 AWS 憑證與權限！"
    exit 1
fi

# ==============================================================================
# 3. 定義服務陣列 (資料夾名稱:ECR倉庫名稱)
# ==============================================================================
# 你可以隨時取消註解來同步更新其他服務
SERVICES=(
    # "asset-service:cloud-native-asset-service"
    # "maintenance:cloud-native-maintenance"
    "user:cloud-native-user"
)

# ==============================================================================
# 4. 迴圈處理每個服務的打包、推送與部署
# ==============================================================================
for SERVICE_INFO in "${SERVICES[@]}"; do
    # 拆分資料夾與倉庫名稱
    DIR="${SERVICE_INFO%%:*}"
    REPO="${SERVICE_INFO##*:}"
    
    # 如果資料夾名稱本身就包含 "-service"，就直接當成 Deployment 名稱；否則才加上 "-service"
    if [[ "$DIR" == *-service ]]; then
        DEPLOYMENT_NAME="${DIR}"
    else
        DEPLOYMENT_NAME="${DIR}-service"
    fi

    echo "------------------------------------------"
    echo "📦 正在處理服務: ${DIR} -> ${REPO}"
    echo "🔄 對應 K8s Deployment: ${DEPLOYMENT_NAME}"
    echo "------------------------------------------"

    # A. 建立 Docker 映像檔
    echo "🛠️  開始建立 Docker 映像檔..."
    # 💡 如果你在 M1/M2/M3 Mac 上開發，但 EKS 節點是 Intel 架構，請將下行取消註解以啟用跨平台編譯：
    # docker build --platform linux/amd64 -t ${REPO}:${VERSION} ./${DIR}
    docker build -t ${REPO}:${VERSION} ./${DIR}

    if [ $? -ne 0 ]; then
        echo "❌ ${DIR} 映像檔建立失敗，跳過此服務。"
        continue
    fi

    # B. 為映像檔加上遠端 ECR 標籤
    echo "🏷️  正在標記 Image Tag..."
    docker tag ${REPO}:${VERSION} ${ECR_REGISTRY}/${REPO}:${VERSION}
    docker tag ${REPO}:${VERSION} ${ECR_REGISTRY}/${REPO}:latest

    # C. 推送到 Amazon ECR
    echo "📤 推送版本 ${VERSION} 到 ECR..."
    docker push ${ECR_REGISTRY}/${REPO}:${VERSION}
    
    echo "📤 推送 latest 版本到 ECR..."
    docker push ${ECR_REGISTRY}/${REPO}:latest

    echo "✨ ECR 推送成功！"

    # D. 自動通知 EKS 執行滾動更新
    echo "🔄 正在通知 AWS EKS 滾動更新 Deployment: ${DEPLOYMENT_NAME}..."
    kubectl rollout restart deployment/${DEPLOYMENT_NAME}
    
    if [ $? -eq 0 ]; then
        echo "⏳ 正在等待 EKS 完成滾動更新部署..."
        # 觀察部署狀態，直到新 Pod 全部 Ready 才會結束該服務的處理
        kubectl rollout status deployment/${DEPLOYMENT_NAME}
        echo "✅ ${DEPLOYMENT_NAME} 已成功在 EKS 上完成更新！"
    else
        echo "❌ 無法通知 EKS 更新，請確認 K8s 叢集連線與 Deployment 名稱是否正確。"
    fi

done

echo "=========================================="
echo "🎉 所有服務處理完畢且已同步至 EKS！"
echo "=========================================="