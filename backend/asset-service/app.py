import os
from flask import Flask, g
from models import db
from equipment_routes import equipment_bp 
# from user_routes import user_bp
from dotenv import load_dotenv
from flasgger import Swagger

# 載入 .env 檔案中的環境變數
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # 初始化 Swagger UI
    app.config['SWAGGER'] = {
        'title': '資產管理系統 (Asset Service) API',
        'uiversion': 3
    }
    Swagger(app)
    
    # 從環境變數取得連線字串，如果沒有設定則拋出錯誤 (Fail Fast)
    database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not database_uri:
        raise ValueError("沒有找到資料庫連線字串！請確保 .env 檔案存在且設定了 SQLALCHEMY_DATABASE_URI")
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    
    # 註冊 API 路由
    app.register_blueprint(equipment_bp)
    # app.register_blueprint(user_bp)

    # 模擬簡單的權限 Middleware (測試用)
    @app.before_request
    def mock_user_auth():
        g.user_id = 1
        g.user_role = 'admin' # 測試期間假設為管理員

    return app

if __name__ == '__main__':
    app = create_app()
    
    # 既然同學已經在 AWS 建立好 DB 和 Table，這裡就不需要 db.create_all() 了
    # 我們可以在啟動前簡單 ping 一下資料庫，確認連線是否成功
    with app.app_context():
        try:
            db.engine.connect()
            print("✅ 成功連線到 AWS MySQL 資料庫！")
        except Exception as e:
            print(f"❌ 資料庫連線失敗：{e}")

    app.run(debug=True, port=5000)
