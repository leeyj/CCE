from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()



class Users(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    passwd = Column(String, nullable=False)
    lv = Column(Integer,nullable=True)
    lastlogin = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    dept = Column(String, nullable=True)  # 새로 추가한 컬럼
    dept_name = Column(String, nullable=True)  # 새로 추가한 컬럼
    up_dept = Column(String, nullable=True)  # 새로 추가한 컬럼


class Depts(Base):
    __tablename__ = 'dept'
    dept = Column(String,primary_key=True)  # 새로 추가한 컬럼
    dept_name = Column(String, nullable=False)  # 새로 추가한 컬럼
    up_dept = Column(String, nullable=False)  # 새로 추가한 컬럼

class UploadFile(Base):
    __tablename__ = 'upload_file'
    id = Column(Integer, primary_key=True)
    filename = Column(String, unique=True)
    upload_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    systems = Column(String, nullable=True)
    reg_name = Column(String, nullable=True)

class IPAddress(Base):
    __tablename__ = 'ip_address'
    id = Column(Integer, primary_key=True)
    upload_file_id = Column(Integer, ForeignKey('upload_file.id'), nullable=False)
    ip = Column(String, nullable=False)

class UploadRecord(Base):
    __tablename__ = 'upload_record'
    id = Column(Integer, primary_key=True)
    upload_file_id = Column(Integer, ForeignKey('upload_file.id'), nullable=False)
    item_id = Column(String(10), nullable=False)
    result = Column(String(20), nullable=False)
    comment = Column(Text)
    data = Column(Text)
    ip = Column(String, nullable=False)
    reg_name = Column(String, nullable=True)

class AssetInfo(Base):
    __tablename__ = 'asset_info'
    id = Column(Integer, primary_key=True, autoincrement=True)
    asset_type = Column(String(20), nullable=False)
    ip_address = Column(String(45), nullable=False)
    platform = Column(String(20), nullable=False)
    purpose = Column(String(100))
    manager_main = Column(String(50))
    manager_sub = Column(String(50))
    memo = Column(Text)

# SQLite 파일명 및 경로
DATABASE_URL = 'sqlite:///uploads.db'

# 엔진 및 세션 생성
engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
session = Session()

# 테이블 생성
Base.metadata.create_all(engine)

print("DB 테이블 생성 완료")



admin_user = session.query(Users).filter_by(id="admin").first()
if not admin_user:
    # passwd 저장방식 주의 (예시에서는 plain text, 실제 운영에서는 해시 사용 권장)
    admin_user = Users(
        id="admin",
        passwd="1234",
        lv=9,
        dept="0000",
        dept_name="root",
        up_dept="0000"
    )
    session.add(admin_user)
    session.commit()
    print("기본 admin 계정 생성 완료")
else:
    print("기본 admin 계정 이미 존재")


normal_user = session.query(Users).filter_by(id="test").first()
if not normal_user:
    normal_user = Users(
        id="test",
        passwd="1234",
        lv=5,
        dept="0001",
        dept_name="Test",
        up_dept="0000"
    )
    session.add(normal_user)
    session.commit()
    print("기본 test 계정 생성 완료")
else:
    print("기본 test 계정 이미 존재")

