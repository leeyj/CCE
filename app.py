import os
import re
from datetime import datetime, timedelta,timezone
from functools import wraps
import logging

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_from_directory
#from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from CCE.models import db, UploadFile, UploadRecord, IPAddress,AssetInfo,Users,Depts
from CCE.upload_processors import *


def create_app():
       
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    

    pattern = re.compile(r'^U-(0[1-9]|[12][0-9]|3[0-6])$')
    logging.basicConfig(level=logging.DEBUG)
    
    @app.before_request
    def log_request_info():
        app.logger.debug(f"Request Path: {request.path}")
        app.logger.debug(f"Request Method: {request.method}")

    @app.after_request
    def log_response_info(response):
        app.logger.debug(f"Response Status: {response.status}")
        return response

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"404 Not Found: {request.path}")
        return "<p>페이지를 찾을 수 없습니다.</p>", 404

    def login_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not session.get('username'):
                flash('로그인이 필요합니다.')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # DB에서 사용자 조회
            user = Users.query.filter_by(id=username).first()

            # 평문 비밀번호 비교
            if user and user.passwd == password:
                # 마지막 로그인 시간 갱신
                user.lastlogin = datetime.now(timezone.utc)
                db.session.commit()

                # Flask 세션에 저장
                session['username'] = username
                flash(f'{username}님 환영합니다.')
                return redirect(url_for('index'))
            else:
                flash('아이디 또는 비밀번호가 올바르지 않습니다.')
            
            
            
            
            
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('로그아웃 되었습니다.')
        return redirect(url_for('login'))

    @app.route('/')
    @login_required
    def index():
        return render_template('index.html')

    @app.route('/xml_upload_content')
    def xml_upload_content():
        return render_template('xml_upload_content.html')

    @app.route('/upload_ajax', methods=['POST'])
    @login_required
    def upload_ajax():
        uploaded_file = request.files.get('xml_file')
        system_type = request.form.get('system', None)
        username = session.get('username')

        if not uploaded_file or not uploaded_file.filename.endswith('.xml'):
            return "<p>유효한 XML 파일을 업로드해주세요.</p>"

        if system_type not in ('linux', 'windows','nginx','apache','db','k8s','docker'):
            return "<p>알 수 없는 시스템 유형입니다.</p>"

        orig_filename = secure_filename(uploaded_file.filename)
        filename = orig_filename
        name, ext = os.path.splitext(orig_filename)

        counter = 1
        while UploadFile.query.filter_by(filename=filename).first() is not None:
            filename = f"{name}_append_{counter}{ext}"
            counter += 1

        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        uploaded_file.save(filepath)

        try:
            if system_type == 'linux':
                return process_linux_upload(username,filepath, filename, system_type)
            elif system_type == 'windows':
                return process_windows_upload(username,filepath, filename, system_type)
            elif system_type == 'nginx':
                return process_nginx_upload(username,filepath, filename, system_type)
            elif system_type == 'apache':
                return process_nginx_upload(username,filepath, filename, system_type)
            elif system_type == 'db':
                return process_db_upload(username,filepath, filename, system_type)
            elif system_type == 'k8s':
                return process_k8s_upload(username,filepath, filename, system_type)
            elif system_type == 'docker':
                return process_docker_upload(username,filepath, filename, system_type)    
        except Exception as e:
            db.session.rollback()
            return f"<p>XML 파싱 중 오류가 발생했습니다: {str(e)}</p>"

    @app.route('/records_content')
    @login_required
    def records_content():
        # 페이지 번호 파라미터 (기본값=1)
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        username = session.get('username')
        user = Users.query.filter_by(id=username).first()
        is_admin = False
        if user and hasattr(user, 'lv') and user.lv == 9:  # lv=9를 admin으로 가정
            is_admin = True
            
        if is_admin:
            # admin은 모든 파일 보여줌
            pagination = UploadFile.query.order_by(UploadFile.upload_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        else:
            # 일반 사용자는 본인 파일만
            pagination = UploadFile.query.filter_by(reg_name=username).order_by(UploadFile.upload_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        files = pagination.items
            
        
        '''
        pagination = UploadFile.query.order_by(UploadFile.upload_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        files = pagination.items
        '''
        
        return render_template('records_content.html', files=files,pagination=pagination)
        

    @app.route('/file_detail')
    @login_required
    def file_detail():
        file_id = request.args.get('file_id', type=int)
        if not file_id:
            return "<p>파일 ID가 필요합니다.</p>"

        upload_file = UploadFile.query.filter_by(id=file_id).first()
        if not upload_file:
            return "<p>존재하지 않는 파일입니다.</p>"

        records = UploadRecord.query.filter_by(upload_file_id=upload_file.id).order_by(UploadRecord.item_id).all()
        if not records:
            return f"<p>파일 '{upload_file.filename}' 에 대한 상세 결과가 없습니다.</p>"

        results = [
            {
                'id': r.item_id,
                'result': r.result,
                'comment': r.comment,
                'data': r.data
            }
            for r in records
        ]

        return render_template('results_content.html', results=results)

    @app.route('/download_content')
    def download_content():
        return render_template('download_content.html')

    @app.route('/download/<path:filename>')
    def download_static(filename):
        download_dir = os.path.join(app.root_path, 'download')
        return send_from_directory(download_dir, filename, as_attachment=True)


    @app.route('/asset_info', methods=['GET', 'POST'])
    @login_required
    def asset_info():
        if request.method == 'POST':
            asset = AssetInfo(
                asset_type=request.form.get('asset_type'),
                ip_address=request.form.get('ip_address'),
                platform=request.form.get('platform'),
                purpose=request.form.get('purpose'),
                manager_main=request.form.get('manager_main'),
                manager_sub=request.form.get('manager_sub'),
                memo=request.form.get('memo')
            )
            db.session.add(asset)
            db.session.commit()
            flash('자산정보가 등록되었습니다.')
            return redirect(url_for('asset_info'))
        assets = AssetInfo.query.order_by(AssetInfo.id.desc()).all()
        return render_template('asset_info.html', assets=assets)

    # 자산정보 삭제
    @app.route('/asset_info/delete/<int:asset_id>', methods=['POST'])
    def asset_delete(asset_id):
        asset = AssetInfo.query.get(asset_id)
        if asset:
            db.session.delete(asset)
            db.session.commit()
            flash('자산정보가 삭제되었습니다.')
        else:
            flash('자산정보를 찾을 수 없습니다.')
        return redirect(url_for('asset_info'))

    # 자산정보 수정 폼
    @app.route('/asset_info/edit/<int:asset_id>', methods=['GET', 'POST'])
    def asset_edit(asset_id):
        asset = AssetInfo.query.get(asset_id)
        if not asset:
            flash('자산정보를 찾을 수 없습니다.')
            return redirect(url_for('asset_info'))

        if request.method == 'POST':
            asset.asset_type = request.form.get('asset_type')
            asset.ip_address = request.form.get('ip_address')
            asset.platform = request.form.get('platform')
            asset.purpose = request.form.get('purpose')
            asset.manager_main = request.form.get('manager_main')
            asset.manager_sub = request.form.get('manager_sub')
            asset.memo = request.form.get('memo')
            db.session.commit()
            flash('자산정보가 수정되었습니다.')
            return redirect(url_for('asset_info'))

        return render_template('asset_edit.html', asset=asset)
    
    @app.route('/user_regi', methods=['GET', 'POST'])
    def user_regi():
        if request.method == 'POST':
            user_id = request.form.get('id')
            lv = request.form.get('lv', type=int)
            passwd = request.form.get('passwd')
            dept = request.form.get('dept')
            dept_name = request.form.get('dept_name')
            up_dept = request.form.get('up_dept')

            if not user_id or not passwd:
                return render_template('user_regi.html', error="아이디와 비밀번호는 필수입니다.")

            if Users.query.get(user_id):
                return render_template('user_regi.html', error="이미 존재하는 사용자 ID입니다.")

            new_user = Users(
                id=user_id,
                lv=lv,
                passwd=passwd,
                lastlogin=datetime.now(timezone.utc),
                dept=dept,
                dept_name=dept_name,
                up_dept=up_dept
            )
            db.session.add(new_user)
            db.session.commit()

            return render_template('user_regi.html', success="사용자 등록이 완료되었습니다.")

        # GET 요청시 폼 렌더링
        return render_template('user_regi.html')
    
    
    
    

    return app
