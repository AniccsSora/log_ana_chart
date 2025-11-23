from flask import Flask, request, render_template, send_file, jsonify
import os
from datetime import datetime
from module import ale_log_analysis as ala


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
    
    # 印出前10行和後10行
    print(f"\n===== {file.filename} =====")
    ala.dump_log(lines)
    
    # 儲存檔案
    file_id = f"{len(processed_files)}_{file.filename}"
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    
    with open(save_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    # 生成下載按鈕名稱
    download_name = f"下載 {file.filename} (已處理)"
    
    # 記錄上傳時間
    upload_time = datetime.now().strftime('%H:%M:%S')
    
    # 判斷測試結果狀態
    filename_lower = file.filename.lower()
    if 'pass' in filename_lower:
        status = 'pass'
    elif 'fail' in filename_lower:
        status = 'fail'
    else:
        status = 'unknown'
    
    processed_files[file_id] = {
        'path': save_path,
        'original_name': file.filename
    }
    
    return jsonify({
        'success': True,
        'filename': file.filename,
        'preview': {
            'head': '\n'.join(lines[:10]),
            'tail': '\n'.join(lines[-10:])
        },
        'file_id': file_id,
        'download_name': download_name,
        'upload_time': upload_time,
        'status': status
    })

@app.route('/download/<file_id>')
def download(file_id):
    if file_id not in processed_files:
        return "檔案不存在", 404
    
    file_info = processed_files[file_id]
    return send_file(file_info['path'], as_attachment=True, download_name=file_info['original_name'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)
