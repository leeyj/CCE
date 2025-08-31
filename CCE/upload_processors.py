import re
import xml.etree.ElementTree as ET
from datetime import datetime
from flask import render_template
from .models import db,UploadFile, UploadRecord, IPAddress

def process_docker_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type,
        reg_name = username
    )
    db.session.add(upload_file)
    db.session.flush()


    ip_text = root.findtext('.//IPAddress', default='').strip()
    ip_addresses = [ip_text] if ip_text else []

    indexk8s = root.findtext('.//index',default='docker').strip()

   
    pattern = re.compile(r'DK-\d{2}')

    results = []
    records_to_add = []
    

    for code in root.findall('.//CODE'):
        code_id = code.get('Id')
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    for record in records_to_add:
        db.session.add(record)

    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        return "<p>DK-01부터 DK-032까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)



def process_k8s_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type,
        reg_name = username
    )
    db.session.add(upload_file)
    db.session.flush()


    ip_text = root.findtext('.//IPAddress', default='').strip()
    ip_addresses = [ip_text] if ip_text else []

    indexk8s = root.findtext('.//index',default='K8S-MASTER').strip()

    if indexk8s == "K8S-MASTER":
        pattern = re.compile(r'KM-\d{2}')
    else:
        pattern = re.compile(r'KW-\d{2}')

    results = []
    records_to_add = []
    

    for code in root.findall('.//CODE'):
        code_id = code.get('Id')
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    for record in records_to_add:
        db.session.add(record)

    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        if indexk8s=="K8S-MASTER":
            return "<p>KM-01부터 KM-017까지 점검 항목 결과가 존재하지 않습니다.</p>"
        else:
            return "<p>KW-01부터 KW-017까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)



def process_db_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type,
        reg_name = username
    )
    db.session.add(upload_file)
    db.session.flush()

    ip_text = root.findtext('IPAddress', default='').strip()
    ip_addresses = [ip_text] if ip_text else []

    results = []
    records_to_add = []
    pattern = re.compile(r'DY-\d{2}')

    for code in root.findall('.//CODE'):
        code_id = code.get('id')
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    for record in records_to_add:
        db.session.add(record)

    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        return "<p>DY-01부터 DY-013까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)




def process_nginx_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type,
        reg_name = username
    )
    db.session.add(upload_file)
    db.session.flush()
    
    ip_addresses = []
    for ip_elem in root.findall('.//ipAddress'):
        text = ip_elem.text.strip() if ip_elem.text else ''
        ips_found = re.findall(r'inet (\d{1,3}(?:\.\d{1,3}){3})', text)
        ip_addresses.extend(ips_found)
    
    results = []
    records_to_add = []
    
    if system_type=="nginx":
        pattern = re.compile(r'WM-\d{2}')
    elif system_type=="apache":
        pattern = re.compile(r'AP-\d{2}')

    for code in root.findall('.//Code'):
        code_id = code.get('id')
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    for record in records_to_add:
        db.session.add(record)

    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        return "<p>WM-01부터 WM-07까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)
    

def process_linux_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type,
        reg_name = username
    )
    db.session.add(upload_file)
    db.session.flush()

    ip_addresses = []
    for ip_elem in root.findall('.//ipAddress'):
        text = ip_elem.text.strip() if ip_elem.text else ''
        ips_found = re.findall(r'inet (\d{1,3}(?:\.\d{1,3}){3})', text)
        ip_addresses.extend(ips_found)

    results = []
    records_to_add = []
    pattern = re.compile(r'U-\d{2}')

    for code in root.findall('.//Code'):
        code_id = code.get('id')
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    for record in records_to_add:
        db.session.add(record)

    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        return "<p>U-01부터 U-036까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)


def process_windows_upload(username,filepath, filename, system_type):
    tree = ET.parse(filepath)
    root = tree.getroot()

    # 업로드 파일 정보 DB 저장
    upload_file = UploadFile(
        filename=filename,
        upload_time=datetime.utcnow(),
        systems=system_type
    )
    db.session.add(upload_file)
    db.session.flush()

    # IPAddress 추출 (루트 아래에 있으므로 바로 찾기)
    ip_text = root.findtext('IPAddress', default='').strip()
    ip_addresses = [ip_text] if ip_text else []

    results = []
    records_to_add = []
    pattern = re.compile(r'PC-\d{2}')

    # XML의 <Code> 태그 처리
    for code in root.findall('.//Code'):
        code_id = code.get('Id')  # XML 속성명은 대소문자 주의!
        if code_id and pattern.match(code_id):
            result_text = code.findtext('Result', default='N/A')
            comment_text = code.findtext('Comment', default='')
            data_elem = code.find('DATA')
            data_text = data_elem.text.strip() if data_elem is not None and data_elem.text else ''
            ip_value = ip_addresses[0] if ip_addresses else None

            record = UploadRecord(
                upload_file_id=upload_file.id,
                item_id=code_id,
                result=result_text,
                comment=comment_text,
                data=data_text,
                ip=ip_value,
                reg_name = username
            )
            records_to_add.append(record)

            results.append({
                'id': code_id,
                'result': result_text,
                'comment': comment_text,
                'data': data_text,
                'ip_addresses': ip_addresses
            })

    # 한번에 DB insert
    for record in records_to_add:
        db.session.add(record)

    # IPAddress 테이블에 저장
    for ip_str in ip_addresses:
        ip_record = IPAddress(upload_file_id=upload_file.id, ip=ip_str)
        db.session.add(ip_record)

    db.session.commit()

    if not results:
        return "<p>PC-01부터 PC-013까지 점검 항목 결과가 존재하지 않습니다.</p>"

    return render_template('results_content.html', results=results, ip_addresses=ip_addresses)
