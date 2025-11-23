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
def root():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>ALE Tools</title>
        <style>
            body { font-family: Arial; max-width: 600px; margin: 100px auto; padding: 20px; text-align: center; }
            h1 { color: #1976D2; }
            .tool-link { 
                display: inline-block;
                background: #4CAF50; 
                color: white; 
                padding: 15px 30px; 
                margin: 10px;
                text-decoration: none; 
                border-radius: 8px;
                font-size: 1.1em;
                transition: all 0.3s;
            }
            .tool-link:hover { 
                background: #45a049;
                transform: scale(1.05);
            }
        </style>
    </head>
    <body>
        <h1>🔧 ALE Tools</h1>
        <p>選擇您要使用的工具：</p>
        <a href="/parselog" class="tool-link">📊 Log Parser</a>
    </body>
    </html>
    '''

@app.route('/parselog')
def parselog():
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
    
    # 確保目錄存在
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 如果有 fail 項目，生成 fail report
    fail_report_path = None
    if parse_result['failed_count'] > 0:
        fail_report_path = save_path.replace('.log', '_fail_report.txt')
        _generate_fail_report(parse_result['failed_sessions'], fail_report_path)
    
    # 生成下載按鈕名稱
    download_name = f"下載 {file.filename}"
    
    # 記錄上傳時間（完整格式）
    upload_time = datetime.now().strftime('%m-%d-%Y %H:%M:%S')
    
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
    
    # 統計所有 command 執行時間（用於折疊區塊）
    command_executions = _collect_command_executions(parse_result['all_sessions'])
    
    # CSV 下載檔名（與原始檔名一致，只改副檔名）
    csv_download_name = file.filename.replace('.log', '_time_stat.csv')
    
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
        'command_executions': command_executions,
        'has_fail_report': fail_report_path is not None,
        'file_id': file_id,
        'download_name': download_name,
        'csv_download_name': csv_download_name,
        'upload_time': upload_time,
        'status': status
    })


def _collect_command_executions(all_sessions: list) -> dict:
    """
    統計每個完整 Command 的所有執行記錄
    
    Returns:
        dict: {
            'Command: diag_tool_info version 1.0.0': [
                {'group': 'test1', 'round': 1, 'start_time': '...', 'duration': 1.23, 'result': 'Pass'},
                {'group': 'test1', 'round': 2, 'start_time': '...', 'duration': 1.45, 'result': 'Pass'}
            ]
        }
    """
    command_map = {}
    
    for session in all_sessions:
        full_command = session.command  # 完整的 Command 字串
        
        if full_command not in command_map:
            command_map[full_command] = []
        
        execution_record = {
            'group': session.group_name,
            'round': session.round_number,
            'start_time': session.start_time,
            'duration': session.duration_seconds,
            'result': session.result,
            'temperature': session.temperature
        }
        command_map[full_command].append(execution_record)
    
    return command_map


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


@app.route('/download_csv/<file_id>')
def download_csv(file_id):
    """下載 command executions CSV"""
    if file_id not in processed_files:
        return "檔案不存在", 404
    
    file_info = processed_files[file_id]
    parse_result = file_info['parse_result']
    
    # 生成 CSV 內容
    csv_lines = []
    csv_lines.append('Command,Group,Round,Start Time,Duration (s),Result,Temperature (°C)')
    
    for session in parse_result['all_sessions']:
        duration_str = f"{session.duration_seconds:.2f}" if session.duration_seconds else ""
        temp_str = str(session.temperature) if session.temperature else ""
        
        # CSV 格式：如果 command 包含逗號，需要用雙引號包起來
        command_escaped = f'"{session.command}"' if ',' in session.command else session.command
        
        csv_lines.append(
            f'{command_escaped},{session.group_name},{session.round_number},'
            f'{session.start_time},{duration_str},{session.result},{temp_str}'
        )
    
    csv_content = '\n'.join(csv_lines)
    
    # 儲存 CSV 檔案
    csv_path = file_info['path'].replace('.log', '_time_stat.csv')
    with open(csv_path, 'w', encoding='utf-8-sig') as f:  # 使用 utf-8-sig 以支援 Excel
        f.write(csv_content)
    
    # 直接使用原始檔名，只替換副檔名
    original_name = file_info['original_name']
    csv_name = original_name.replace('.log', '_time_stat.csv')
    
    return send_file(csv_path, as_attachment=True, download_name=csv_name)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
