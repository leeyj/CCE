from flask_sqlalchemy import SQLAlchemy



db = SQLAlchemy()

class UploadFile(db.Model):
    __tablename__ = 'upload_file'
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, unique=True)
    upload_time = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    systems = db.Column(db.String, nullable=True)  # 새로 추가한 컬럼
    ip_addresses = db.relationship('IPAddress', backref='upload_file', cascade='all, delete-orphan')

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
