# 🌅 EKS 每日早晨啟動手冊 (Morning Guide)

這份手冊將引導你按順序執行腳本，以最快速度回復開發環境。

## 🚀 啟動流程 (預計耗時: 15-20 分鐘)

### Step 1: 建立 EKS 叢集

在專案根目錄下執行。這會啟動控制平面與工作節點。

```bash
./create_eks_cluster.sh

```

*註：此步驟最久，建議執行後先去泡杯咖啡。*

### Step 2: 初始化 K8s Secrets

進入 `backend` 資料夾，將 `.env` 中的環境變數同步至叢集。

```bash
cd backend
./init_k8s_secrets.sh

```

### Step 3: 部署基礎服務與 ALB

同樣在 `backend` 資料夾下，先部署 K8s 物件，再設定負載平衡器。

```bash
# 1. 部署各個服務的 Deployment 與 Service
kubectl apply -f k8s/asset-service.yaml -f k8s/maintenance.yaml -f k8s/user.yaml

# 2. 設定 ALB Controller 與 Ingress (這會自動建立 AWS ALB)
./setup-alb.sh

```

*註：當 Ingress 成功獲取 `ADDRESS` 後，代表 AWS ALB 已經建立完成且與 Kubernetes Ingress 成功綁定。*

### Step 4: 同步最新程式碼 (選用)

如果你有修改程式碼，或者想確保 ECR 映像檔與 K8s 狀態同步：

```bash
./deploy_ecr_eks.sh

```

---

## 🔍 如何檢查狀態？

1. **檢查節點：** `kubectl get nodes` (應看到 2 個 Ready 的節點)
2. **檢查 Pods：** `kubectl get pods` (所有服務應為 Running)
3. **取得 ALB 網址：**
```bash
kubectl get ingress -w

```


輸出範例：

```bash
   NAME                   CLASS    HOSTS   ADDRESS                                                                 PORTS   AGE
   cloud-native-ingress   <none>   *       k8s-default-cloudnat-1c2eb072ff-674129447.ap-east-2.elb.amazonaws.com   80      102s

```

*複製 `ADDRESS` 欄位的網址，即可用於 Browser 或 cURL 測試。*

---

## 💡 開發者心法：ALB 建立後的 DNS 盲區

即使 `kubectl get ingress` 已經顯示了 ALB 的 ADDRESS，**DNS 通常還需要等待約 3 ~ 5 分鐘進行全球傳播（Propagation）。**

### 1. 剛建立就立刻 cURL 失敗？

```bash
curl -X GET http://<YOUR-ALB-ADDRESS>/api/users/users_test_s3
# 錯誤訊息：curl: (6) Could not resolve host

```

別慌！這代表 Domain name 還找不到對應的 IP，屬於正常現象。

### 2. 使用 `nslookup` 工具驗證 DNS 狀態

你可以定時執行以下指令來確認 DNS 好了沒：

```bash
nslookup <YOUR-ALB-ADDRESS>

```

* **如果看到 `NXDOMAIN`：**
代表 DNS record 尚不存在，傳播尚未完成，請再等等。
* **如果看到類似下方的多個 IP 回傳：**

```bash
  Non-authoritative answer:
  Name:   k8s-default-cloudnat-1c2eb072ff-674129447.ap-east-2.elb.amazonaws.com
  Address: 43.212.157.175
  Address: 43.213.254.74
  Address: 43.213.24.183

```

這代表 DNS 解析成功！此時再次執行 `curl` 即可順利連線。

> **為什麼會有那麼多 IP？**
> AWS Application Load Balancer 本身是分布式系統，會同時部署在多個可用區（Availability Zone）以達到**高可用性（High Availability）、負載平衡（Load Balancing）與容錯（Fault Tolerance）**。每個節點都有獨立的 Public IP，所以會解析出多個結果。

### 測試
```
curl -i --doh-url https://cloudflare-dns.com/dns-query http://angrysquirrel.qzz.io/api/user/users_test_s3
```

---

## 🌙 晚上如何關閉？

為了省錢，下班前請務必執行根目錄下的腳本，將 AWS 資源完整釋放：

```bash
./destroy_eks_cluster.sh

```

```</YOUR-ALB-ADDRESS></YOUR-ALB-ADDRESS>

```