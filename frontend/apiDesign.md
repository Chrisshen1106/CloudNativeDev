# API 設計文件

---

## 一、一般員工（資產持有人 user）API 對接

### 1. 登入
- `POST /api/login`
- **Request JSON**：
  ```json
  {
    "account": "wang@company.com",
    "password": "your_password"
  }
  ```
- **Response JSON**：
  ```json
  {
    "id": "U001",
    "name": "王小明",
    "role": "user/manager",
    "department": "研發部",
    "email": "wang@company.com",
    "token": "jwt_token" 
  }
  ```

### 2. 取得個人資產列表
- `GET /api/assets?mine=true&keyword=&category=&status=&page=1&pageSize=20`
- **Response JSON**：
  ```json
  {
    "total": 2,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": "A001",
        "assetNumber": "AST-2024-001",
        "name": "MacBook Pro 16\"",
        "category": "computer",
        "model": "MacBook Pro M3 Max",
        "location": "台北總部 3F-A302",
        "department": "研發部",
        "status": "normal"
      }
    ]
  }
  ```

### 3. 取得資產詳情
- `GET /api/assets/{id}`
- **Response JSON**：
  ```json
  {
    "id": "A001",
    "assetNumber": "AST-2024-001",
    "name": "MacBook Pro 16\"",
    "category": "computer",
    "model": "MacBook Pro M3 Max",
    "specs": "48GB RAM, 1TB SSD",
    "serialNumber": "C02XG2JHJGH5",
    "supplier": "Apple Taiwan",
    "purchaseDate": "2024-01-15",
    "purchasePrice": 89900,
    "location": "台北總部 3F-A302",
    "ownerId": "U001",
    "department": "研發部",
    "activationDate": "2024-01-20",
    "warrantyExpiry": "2027-01-20",
    "status": "normal",
    "notes": "",
    "maintenanceHistory": [
      {
        "id": "REQ-2024-003",
        "status": "completed",
        "requestDate": "2024-02-10",
        "faultDescription": "MacBook 鍵盤按鍵失靈...",
        "reviewerId": "U005",
        "reviewerName": "黃桂昱",
        "reviewDate": "2024-02-11",
        "reviewNote": "已確認問題，安排送修。",
        "repairDate": "2024-02-13",
        "repairContent": "鍵盤按鍵機械結構損壞...",
        "repairSolution": "更換整片鍵盤模組",
        "repairCost": 3500,
        "completionDate": "2024-02-20"
      }
    ]
  }
  ```

### 4. 送出維修申請
- `POST /api/requests`
- **Request JSON**：
  ```json
  {
    "assetId": "A001",
    "faultDescription": "MacBook 鍵盤按鍵失靈...",
    "attachments": ["url1", "url2"]
  }
  ```
- **Response JSON**：
  ```json
  {
    "id": "REQ-2024-009",
    "status": "pending"
  }
  ```


### 5. 取得維修申請單列表
- `GET /api/requests?status=&keyword=&page=1&pageSize=20`
  - 一般員工：只會回傳自己的申請單
  - 管理者：會回傳所有人的申請單，且每筆資料會有 requesterId
- **Response JSON**：
  ```json
  {
    "total": 2,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": "REQ-2024-003",
        "assetId": "A001",
        "requesterId": "U001",
        "faultDescription": "MacBook 鍵盤按鍵失靈...",
        "status": "completed",
        "requestDate": "2024-02-10"
      }
    ]
  }
  ```

### 6. 取得維修申請單詳情
- `GET /api/requests/{id}`
- **Response JSON**：
  ```json
  {
    "id": "REQ-2024-003",
    "assetId": "A001",
    "requesterId": "U001",
    "faultDescription": "MacBook 鍵盤按鍵失靈...",
    "status": "completed",
    "requestDate": "2024-02-10",
    "attachments": [],
    "reviewerId": "U005",
    "reviewDate": "2024-02-11",
    "reviewNote": "已確認問題，安排送修。",
    "repairDate": "2024-02-13",
    "repairContent": "鍵盤按鍵機械結構損壞...",
    "repairSolution": "更換整片鍵盤模組",
    "repairCost": 3500,
    "repairPersonnel": "Apple 授權維修中心",
    "completionDate": "2024-02-20"
  }
  ```

---

## 二、資產管理者（Manager）API 對接

### 1. 取得所有資產列表
- `GET /api/assets?keyword=&category=&status=&page=1&pageSize=20`
- **Response JSON**：
  ```json
  {
    "total": 10,
    "page": 1,
    "pageSize": 20,
    "items": [
      {
        "id": "A001",
        "assetNumber": "AST-2024-001",
        "name": "MacBook Pro 16\"",
        "category": "computer",
        "model": "MacBook Pro M3 Max",
        "location": "台北總部 3F-A302",
        "ownerId": "U001",
        "department": "研發部",
        "status": "normal"
      }
    ]
  }
  ```

### 2. 新增資產
- `POST /api/assets`
- **Request JSON**：
  ```json
  {
    "name": "HP 雷射印表機",              
    "category": "printer",                
    "status": "normal",                
    "model": "HP LaserJet Pro M404dn",   
    "specs": "黑白雷射, 雙面列印",        
    "serialNumber": "HPLJ123456",      
    "notes": "",                        
    "supplier": "HP Taiwan",              
    "purchasePrice": 12000,            
    "purchaseDate": "2024-04-01",      
    "activationDate": "2024-04-05",    
    "warrantyExpiry": "2027-04-05",       
    "location": "新竹辦公室 2F-B201",     
    "ownerId": "U002",                    
    "department": "業務部"              
  }
  ```
- **Response JSON**：
  ```json
  {
    "id": "A010"
  }
  ```

### 3. 編輯資產
- `PUT /api/assets/{id}`
- 我不太確定這支API該怎麼設計，請後端協助

### 4. 刪除資產
- `DELETE /api/assets/{id}`
- **Response JSON**：
  ```json
  { "success": true }
  ```

### 5. 取得所有維修申請單列表
- `GET /api/requests?status=&keyword=&page=1&pageSize=20`
- **Response JSON**：同 user 端，但會有所有人的申請單，且可見 requesterId

### 6. 取得維修申請單詳情
- `GET /api/requests/{id}`
- **Response JSON**：同 user 端，但可見 reviewerId、reviewDate、reviewNote、repairDate、repairContent、repairSolution、repairCost、repairPersonnel、completionDate

### 7. 審核維修申請
- `PUT /api/requests/{id}/review`
- **Request JSON**：
  ```json
  {
    "status": "approved", // 或 "rejected"
    "reviewNote": "同意送修，請盡速安排。"
  }
  ```
- **Response JSON**：
  ```json
  { "success": true }
  ```

### 8. 維修完成/結案
- `PUT /api/requests/{id}/complete`
- **Request JSON**：
  ```json
  {
    "repairContent": "更換螢幕模組",
    "repairSolution": "原廠零件更換",
    "repairCost": 8500,
    "repairPersonnel": "Apple 授權維修中心"
  }
  ```
- **Response JSON**：
  ```json
  { "success": true }
  ```

---

> 若有新功能需求，請於本檔案補充。
