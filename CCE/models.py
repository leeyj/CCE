from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()


class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String, primary_key=True)
    lv = db.Column(db.Integer)
    passwd = db.Column(db.String,nullable=False)
    lastlogin = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    dept = db.Column(db.String, nullable=True)  # 새로 추가한 컬럼
    dept_name = db.Column(db.String, nullable=True)  # 새로 추가한 컬럼
    up_dept = db.Column(db.String, nullable=True)  # 새로 추가한 컬럼


class Depts(db.Model):
    __tablename__ = 'dept'
    dept = db.Column(db.String, primary_key=True)  # 새로 추가한 컬럼
    dept_name = db.Column(db.String, nullable=False)  # 새로 추가한 컬럼
    up_dept = db.Column(db.String, nullable=False)  # 새로 추가한 컬럼



class UploadFile(db.Model):
    __tablename__ = 'upload_file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, unique=True)
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    systems = db.Column(db.String, nullable=True)  # 새로 추가한 컬럼
    ip_addresses = db.relationship('IPAddress', backref='upload_file', cascade='all, delete-orphan')
    reg_name = db.Column(db.String, nullable=True)

class IPAddress(db.Model):
    __tablename__ = 'ip_address'
    id = db.Column(db.Integer, primary_key=True)
    upload_file_id = db.Column(db.Integer, db.ForeignKey('upload_file.id'), nullable=False)
    ip = db.Column(db.String, nullable=False)

class UploadRecord(db.Model):
    __tablename__ = 'upload_record'
    id = db.Column(db.Integer, primary_key=True)
    upload_file_id = db.Column(db.Integer, db.ForeignKey('upload_file.id'), nullable=False)
    item_id = db.Column(db.String(10), nullable=False)
    result = db.Column(db.String(20), nullable=False)
    comment = db.Column(db.Text)
    data = db.Column(db.Text)
    ip = db.Column(db.String, nullable=False)
    reg_name = db.Column(db.String, nullable=True)
    


class AssetInfo(db.Model):
    __tablename__ = 'asset_info'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)       # 순번 (자동)
    asset_type = db.Column(db.String(20), nullable=False)                  # 자산종류 (server/cloud)
    ip_address = db.Column(db.String(45), nullable=False)                  # IP
    platform = db.Column(db.String(20), nullable=False)                    # 플렛폼
    purpose = db.Column(db.String(100))                                    # 용도
    manager_main = db.Column(db.String(50))                                # 관리자(정)
    manager_sub = db.Column(db.String(50))                                 # 관리자(부)
    memo = db.Column(db.Text)                                              # 메모

