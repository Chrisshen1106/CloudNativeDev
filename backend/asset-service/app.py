import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from models import db
from equipment_routes import equipment_bp
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)

    database_uri = os.environ.get('SQLALCHEMY_DATABASE_URI')
    if not database_uri:
        raise ValueError("沒有找到資料庫連線字串！請確保 .env 檔案存在且設定了 SQLALCHEMY_DATABASE_URI")

    app.json.ensure_ascii = False
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

    db.init_app(app)
    JWTManager(app)

    app.register_blueprint(equipment_bp)

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"message": "找不到資源"}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"message": "不支援此 HTTP 方法"}), 405

    return app

app = create_app()

if __name__ == '__main__':
    # 啟動前簡單 ping 一下資料庫，確認連線是否成功
    with app.app_context():
        try:
            db.engine.connect()
            print("✅ 成功連線到 AWS MySQL 資料庫！")
        except Exception as e:
            print(f"❌ 資料庫連線失敗：{e}")

    app.run(debug=True, port=5000)
