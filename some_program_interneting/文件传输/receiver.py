import os
import socket
import threading
import struct

# 获取本机的局域网 IP 地址
def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
    finally:
        s.close()
    return local_ip

# 服务器配置
SERVER_HOST = get_local_ip()
SERVER_PORT = 12345
BUFFER_SIZE = 65536
BASE_DIR = './server_files'

# 创建文件存储目录
os.makedirs(BASE_DIR, exist_ok=True)

def handle_client(client_socket, client_address):
    print(f"[INFO] 客户端 {client_address} 已连接")
    try:
        while True:
            command = client_socket.recv(BUFFER_SIZE).decode()
            if not command:
                break

            if command == 'LIST':
                files = os.listdir(BASE_DIR)
                if files:
                    response = "\n".join(files)
                else:
                    response = "文件夹为空"
                print(f"[INFO] 客户端请求文件列表")
                client_socket.send(response.encode())

            elif command.startswith('DOWNLOAD'):
                _, filename = command.split()
                filepath = os.path.join(BASE_DIR, filename)
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)

                    # 发送文件大小（8 个字节）
                    client_socket.send(struct.pack('Q', file_size))
                    print(f"[INFO] 开始发送文件: {filename}，大小: {file_size} 字节")

                    # 发送文件内容
                    with open(filepath, 'rb') as f:
                        while chunk := f.read(BUFFER_SIZE):
                            client_socket.send(chunk)
                    print(f"[INFO] 文件 {filename} 发送完成")
                else:
                    # 文件不存在时发送错误消息
                    error_message = "ERROR: File not found"
                    client_socket.send(error_message.encode())
                    print(f"[WARNING] 文件 {filename} 不存在")

            else:
                client_socket.send(b'ERROR: Invalid command')
    except Exception as e:
        print(f"[ERROR] 客户端 {client_address} 处理错误：{e}")
    finally:
        client_socket.close()
        print(f"[INFO] 客户端 {client_address} 已断开连接")

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[INFO] 服务器已启动，监听 {SERVER_HOST}:{SERVER_PORT}")
    while True:
        client_socket, client_address = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    start_server()
