from flask import Flask, render_template, request, redirect, url_for, flash
import secrets
from packet_capture import capture_packets, classify_packets, decode_packet, save_packet, filter_packets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # 随机生成一个 16 字节的密钥

# 模拟用户数据
users = {
    'admin': '123456'
}

def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if authenticate(username, password):
        flash('登录成功！', 'success')
        return redirect(url_for('dashboard'))
    else:
        flash('无效的凭据', 'danger')
        return redirect(url_for('home'))

@app.route('/dashboard')
def dashboard():
    packets = capture_packets()
    stats = classify_packets(packets)
    for packet in packets:
        save_packet(packet)  # 保存每个捕获的数据包
    return render_template('home.html', packets=packets, stats=stats)

@app.route('/decode/<int:packet_id>')
def decode(packet_id):
    packets = capture_packets()
    packet = packets[packet_id]
    decoded_packet = decode_packet(packet)
    return render_template('decode.html', packet=decoded_packet)

if __name__ == "__main__":
    app.run(debug=True)