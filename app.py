import os
import re
from datetime import datetime, timedelta
from functools import wraps
import logging

from flask import Flask, render_template, request, redirect, url_for, session, flash, make_response, send_from_directory
#from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename

from CCE.models import db, UploadFile, UploadRecord, IPAddress
from CCE.upload_processors import process_linux_upload, process_windows_upload,process_nginx_upload


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
            USERS = {'admin': 'password123'}
            if username in USERS and USERS[username] == password:
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

        if not uploaded_file or not uploaded_file.filename.endswith('.xml'):
            return "<p>유효한 XML 파일을 업로드해주세요.</p>"

        if system_type not in ('linux', 'windows','nginx','apache'):
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
                return process_linux_upload(filepath, filename, system_type)
            elif system_type == 'windows':
                return process_windows_upload(filepath, filename, system_type)
            elif system_type == 'nginx':
                return process_nginx_upload(filepath, filename, system_type)
            elif system_type == 'apache':
                return process_nginx_upload(filepath, filename, system_type)
        except Exception as e:
            db.session.rollback()
            return f"<p>XML 파싱 중 오류가 발생했습니다: {str(e)}</p>"

    @app.route('/records_content')
    @login_required
    def records_content():
        # 페이지 번호 파라미터 (기본값=1)
        page = request.args.get('page', 1, type=int)
        per_page = 20
        
        pagination = UploadFile.query.order_by(UploadFile.upload_time.desc()).paginate(page=page, per_page=per_page, error_out=False)
        files = pagination.items
        '''
        files = UploadFile.query.order_by(UploadFile.upload_time.desc()).limit(50).all()
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

    return app
