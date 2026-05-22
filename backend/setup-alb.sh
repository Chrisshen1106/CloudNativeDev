# setup-alb-sh
#!/bin/bash

# ==============================================================================
# 配置變數
# ==============================================================================
CLUSTER_NAME="cloud-native"
AWS_REGION="ap-east-2"
AWS_ACCOUNT_ID="794934876006"
POLICY_NAME="AWSLoadBalancerControllerIAMPolicy"
POLICY_ARN="arn:aws:iam::${AWS_ACCOUNT_ID}:policy/${POLICY_NAME}"
INGRESS_FILE="k8s/ingress.yaml"  

echo "===================================================="
echo "🛠️  開始初始化 AWS EKS ALB 負載平衡器環境..."
echo "📂 目標 Ingress 檔案: ${INGRESS_FILE}"
echo "===================================================="

# ------------------------------------------------------------------------------
# 防呆檢查
# ------------------------------------------------------------------------------
if [ ! -f "$INGRESS_FILE" ]; then
    echo "❌ 錯誤：找不到 ${INGRESS_FILE} 檔案！"
    exit 1
fi

if ! command -v helm &> /dev/null; then
    echo "❌ 錯誤：本地電腦尚未安裝 helm，請先執行 'brew install helm' 進行安裝！"
    exit 1
fi

# ------------------------------------------------------------------------------
# 🔍 核心防呆：自動確認並建立 AWS IAM Policy
# ------------------------------------------------------------------------------
echo "🔍 正在檢查 AWS 帳戶中是否存在 IAM Policy [${POLICY_NAME}]..."

aws iam get-policy --policy-arn ${POLICY_ARN} > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "ℹ️  通知：偵測到 [${POLICY_NAME}] 已存在於您的 AWS 帳戶中，跳過建立步驟。"
else
    echo "⚠️  警告：找不到該 Policy！即將開始自動下載官方規格並進行建立..."
    
    curl -sS -O https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
    
    if [ ! -f "iam_policy.json" ]; then
        echo "❌ 錯誤：無法從 GitHub 下載 iam_policy.json，請檢查網路連線！"
        exit 1
    fi

    aws iam create-policy \
      --policy-name ${POLICY_NAME} \
      --policy-document file://iam_policy.json
    
    if [ $? -eq 0 ]; then
        echo "✅ 成功建立全域 IAM Policy: ${POLICY_ARN}"
        rm -f iam_policy.json
    else
        echo "❌ 錯誤：建立 IAM Policy 失敗！"
        exit 1
    fi
fi

# ==============================================================================
# 1. 關聯 OIDC 識別提供者
# ==============================================================================
echo "🔗 1. 正在為叢集啟用 OIDC 身分驗證器..."
eksctl utils associate-iam-oidc-provider \
    --cluster=${CLUSTER_NAME} \
    --region=${AWS_REGION} \
    --approve

if [ $? -ne 0 ]; then
    echo "❌ OIDC 啟用失敗，請確認叢集狀態！"
    exit 1
fi

# ==============================================================================
# 2. 建立 K8s ServiceAccount 並綁定 IAM Role (IRSA)
# ==============================================================================
echo "🔑 2. 正在建立 K8s ServiceAccount 並綁定 IAM 角色..."
eksctl delete iamserviceaccount --cluster=${CLUSTER_NAME} --region=${AWS_REGION} --namespace=kube-system --name=aws-load-balancer-controller > /dev/null 2>&1

eksctl create iamserviceaccount \
    --cluster=${CLUSTER_NAME} \
    --namespace=kube-system \
    --name=aws-load-balancer-controller \
    --role-name AmazonEKSLoadBalancerControllerRole \
    --attach-policy-arn=${POLICY_ARN} \
    --approve \
    --region=${AWS_REGION}

if [ $? -ne 0 ]; then
    echo "❌ ServiceAccount 建立失敗！"
    exit 1
fi

# ==============================================================================
# 3. 使用 Helm 安裝 AWS Load Balancer Controller
# ==============================================================================
echo "📦 3. 正在透過 Helm 安裝 AWS Load Balancer Controller..."

helm repo add eks https://aws.github.io/eks-charts
helm repo update eks

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
    -n kube-system \
    --set clusterName=${CLUSTER_NAME} \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-load-balancer-controller

if [ $? -ne 0 ]; then
    echo "❌ Helm 安裝 Controller 失敗！"
    exit 1
fi

echo "⏳ 正在等待 Controller 部署就緒..."
kubectl rollout status deployment/aws-load-balancer-controller -n kube-system --timeout=90s

if [ $? -ne 0 ]; then
    echo "❌ Controller Pod 在規定時間內未就緒！"
    exit 1
fi

echo "✅ AWS Load Balancer Controller 已成功在集群中啟動！"

# ==============================================================================
# 4. 自動套用 Ingress 路由規則（建立 ALB）
# ==============================================================================
echo "🌐 4. 正在部署 Ingress 路由規則表 (${INGRESS_FILE})..."
kubectl apply -f $INGRESS_FILE

echo "===================================================="
echo "🎉 恭喜！ALB 環境已全部部署完畢！"
echo "🔍 請執行以下指令來追蹤你的公網 ALB 網址（Address）："
echo "   kubectl get ingress -w"
echo ""
echo "💡 拿到 ADDRESS 欄位那串 xxx.elb.amazonaws.com 網址後："
echo "   請將它貼進 CloudFront Distribution 的 Origin 中，完成前後端對接！"
echo "===================================================="