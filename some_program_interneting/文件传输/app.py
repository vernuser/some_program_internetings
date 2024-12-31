from flask import Flask, render_template, request, send_from_directory, flash, jsonify
import os

app = Flask(__name__)

# 配置上传文件存储路径
UPLOAD_FOLDER = './server_files'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # 如果文件夹不存在，则创建
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'your_secret_key'

@app.route('/')
def index():
    """主页：选择发送方或接收方"""
    return render_template('index.html')

@app.route('/sender', methods=['GET', 'POST'])
def sender():
    """发送方界面：上传、下载和查看文件列表"""
    if request.method == 'POST':
        # 处理文件上传
        if 'file' in request.files:
            file = request.files['file']
            if file.filename == '':
                flash('未选择文件！', 'danger')
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                if os.path.exists(filepath):
                    flash(f'文件 {file.filename} 已存在！', 'warning')
                else:
                    file.save(filepath)
                    flash(f'文件 {file.filename} 上传成功！', 'success')

    return render_template('sender.html')

@app.route('/receiver', methods=['GET'])
def receiver():
    """接收方界面：查看文件列表"""
    return render_template('receiver.html')

@app.route('/get_files', methods=['GET'])
def get_files():
    """获取服务器中文件列表"""
    files = os.listdir(UPLOAD_FOLDER)  # 列出文件夹中的所有文件
    return jsonify(files)

@app.route('/download/<filename>', methods=['GET'])
def download_file(filename):
    """下载指定文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
