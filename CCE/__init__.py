from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # 설정 파일 로드 (필요하면)
    app.config.from_pyfile('config.py')

    # DB 초기화
    db.init_app(app)

    # 라우트(블루프린트) 등록
    # from CCE.views import main_blueprint
    # app.register_blueprint(main_blueprint)

    return app
