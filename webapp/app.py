from flask import Flask, request, render_template, send_file, jsonify
import os
from datetime import datetime
from module import test_session_parser as tsp


app = Flask(__name__)

# 根據今天日期建立上傳資料夾
today_folder = datetime.now().strftime('%m_%d_%Y')
app.config['UPLOAD_FOLDER'] = os.path.join('uploads', today_folder)
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 儲存已處理的檔案資訊
processed_files = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '沒有檔案'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': '檔案名稱為空'})
    
    # 讀取檔案內容
    content = file.read().decode('utf-8', errors='ignore')
    lines = content.splitlines()
    
    # 解析 log 檔案
    print(f"\n===== 開始解析: {file.filename} =====")
    parse_result = tsp.parse_diag_log(lines)

    print("============================================")
    print(f"解析結果: {file.filename}")
    print(f"上傳時間: {datetime.now().strftime('%m-%d %H:%M:%S')}")
    print(f"測試開始時間: {parse_result['test_start_time']}")
    print(f"總測試項目: {parse_result['total_sessions']}")
    print(f"Pass: {parse_result['passed_count']}")
    print(f"Fail: {parse_result['failed_count']}")
    print(f"Exception: {parse_result['exception_count']}")
    print(f"===========================================")
    # 儲存檔案
    file_id = f"{int(datetime.now().timestamp() * 1000)}_{file.filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 如果有 fail 項目，生成 fail report
    fail_report_path = None
    if parse_result['failed_count'] > 0:
        fail_report_path = save_path.replace('.log', '_fail_report.txt')
        _generate_fail_report(parse_result['failed_sessions'], fail_report_path)
    
    # 生成下載按鈕名稱
    download_name = f"下載 {file.filename}"
    
    # 記錄上傳時間
    upload_time = datetime.now().strftime('%H:%M:%S')
    
    # 判斷測試結果狀態
    if parse_result['failed_count'] > 0:
        status = 'fail'
    elif parse_result['exception_count'] > 0:
        status = 'unknown'
    else:
        status = 'pass'
    
    processed_files[file_id] = {
        'path': save_path,
        'original_name': file.filename,
        'parse_result': parse_result,
        'fail_report_path': fail_report_path
    }
    
    # 準備 failed sessions 的摘要資訊
    failed_summaries = []
    for session in parse_result['failed_sessions'][:10]:  # 只傳前10個
        summary = {
            'command': session.command_name,
            'group': session.group_name,
            'round': session.round_number,
            'start_time': session.start_time,
            'temperature': session.temperature,
            'log_full': '\n'.join(session.log_content)  # 完整 log 包含 Result 和 End time
        }
        failed_summaries.append(summary)
    
    return jsonify({
        'success': True,
        'filename': file.filename,
        'test_info': {
            'start_time': parse_result['test_start_time'],
            'total_sessions': parse_result['total_sessions'],
            'passed': parse_result['passed_count'],
            'failed': parse_result['failed_count'],
            'exception': parse_result['exception_count']
        },
        'failed_summaries': failed_summaries,
        'has_fail_report': fail_report_path is not None,
        'file_id': file_id,
        'download_name': download_name,
        'upload_time': upload_time,
        'status': status
    })


def _generate_fail_report(failed_sessions: list, output_path: str):
    """生成 fail report 文字檔"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FAILED SESSIONS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        for i, session in enumerate(failed_sessions, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"FAILED SESSION #{i}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Group: {session.group_name} | Round: {session.round_number}\n")
            f.write(f"Command: {session.command}\n")
            f.write(f"Start Time: {session.start_time}\n")
            f.write(f"End Time: {session.end_time}\n")
            if session.temperature:
                f.write(f"Temperature: {session.temperature} °C\n")
            if session.duration_seconds:
                f.write(f"Duration: {session.duration_seconds:.2f} seconds\n")
            f.write(f"\n--- LOG CONTENT ---\n")
            f.write('\n'.join(session.log_content))
            f.write(f"\n\n")
        
        f.write(f"\n{'=' * 80}\n")
        f.write(f"Total Failed Sessions: {len(failed_sessions)}\n")
        f.write(f"{'=' * 80}\n")

@app.route('/download/<file_id>')
def download(file_id):
    if file_id not in processed_files:
        return "檔案不存在", 404
    
    file_info = processed_files[file_id]
    return send_file(file_info['path'], as_attachment=True, download_name=file_info['original_name'])


@app.route('/download_fail_report/<file_id>')
def download_fail_report(file_id):
    """下載 fail report"""
    if file_id not in processed_files:
        return "檔案不存在", 404
    
    file_info = processed_files[file_id]
    if not file_info.get('fail_report_path'):
        return "無 fail report", 404
    
    report_name = file_info['original_name'].replace('.log', '_fail_report.txt')
    return send_file(file_info['fail_report_path'], as_attachment=True, download_name=report_name)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
