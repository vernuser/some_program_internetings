import os
import socket
import struct

# 客户端配置
SERVER_HOST = input("请输入服务器局域网 IP 地址：").strip()
SERVER_PORT = 12345
BUFFER_SIZE = 65536
UPLOAD_DIR = './client_uploads'
DOWNLOAD_DIR = './client_downloads'

# 创建文件存储目录
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def connect_to_server():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))
    return client_socket

def list_files(client_socket):
    client_socket.send(b"LIST")
    response = client_socket.recv(BUFFER_SIZE).decode()
    print("\n服务器文件列表：\n" + response)

def upload_file(client_socket, filename):
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[ERROR] 文件 '{filename}' 不存在于本地上传目录，请检查文件路径。")
        return

    file_size = os.path.getsize(filepath)
    client_socket.send(f"UPLOAD {filename}".encode())  # 命令 + 文件名
    client_socket.send(struct.pack('Q', file_size))  # 文件大小
    print(f"[INFO] 开始上传文件: {filename}, 大小: {file_size / 1024:.2f} KB")

    with open(filepath, 'rb') as f:
        while chunk := f.read(BUFFER_SIZE):
            client_socket.send(chunk)

    # 接收服务器反馈
    response = client_socket.recv(BUFFER_SIZE).decode()
    if response == 'UPLOAD_SUCCESS':
        print(f"[INFO] 文件 {filename} 上传成功。")
    else:
        print(f"[ERROR] 文件 {filename} 上传失败。")

def download_file(client_socket, filename):
    # 检查本地是否存在同名文件
    local_file_path = os.path.join(DOWNLOAD_DIR, filename)
    if os.path.exists(local_file_path):
        print(f"[WARNING] 文件 '{filename}' 已存在于本地下载目录。")
        choice = input("是否覆盖文件？输入 'Y' 表示覆盖，输入 'N' 表示重命名后下载：").strip().upper()
        if choice == 'N':
            # 生成新的文件名（加上数字后缀）
            base, ext = os.path.splitext(filename)
            counter = 1
            while True:
                new_filename = f"{base}_{counter}{ext}"
                new_path = os.path.join(DOWNLOAD_DIR, new_filename)
                if not os.path.exists(new_path):
                    local_file_path = new_path
                    print(f"[INFO] 新文件名为: {new_filename}")
                    break
                counter += 1
        elif choice != 'Y':
            print("[INFO] 用户取消下载操作。")
            return

    client_socket.send(f"DOWNLOAD {filename}".encode())
    response = client_socket.recv(8)  # 尝试接收文件大小（8 个字节）

    # 检查是否正确接收到文件大小
    if len(response) != 8:
        error_message = response.decode()
        print(f"[ERROR] {error_message}")
        return

    # 如果是 8 字节，解析为文件大小
    file_size = struct.unpack('Q', response)[0]
    received_size = 0

    with open(local_file_path, 'wb') as f:
        print(f"[INFO] 开始下载文件 {filename}, 大小: {file_size / 1024:.2f} KB")
        while received_size < file_size:
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                break
            f.write(data)
            received_size += len(data)

    if received_size == file_size:
        print(f"[INFO] 文件 {filename} 下载成功，文件大小正确，存储路径: {local_file_path}")
    else:
        print(f"[ERROR] 文件 {filename} 下载不完整，请重试。")

def main():
    client_socket = connect_to_server()
    print(f"[INFO] 已连接到服务器 {SERVER_HOST}:{SERVER_PORT}\n")

    while True:
        print("\n请选择操作：")
        print("1. 查看服务器文件列表")
        print("2. 上传文件")
        print("3. 下载文件")
        print("4. 退出")

        try:
            choice = int(input("输入数字编号："))
        except ValueError:
            print("[ERROR] 无效输入，请输入有效数字。")
            continue

        if choice == 1:
            list_files(client_socket)
        elif choice == 2:
            filename = input("请输入要上传的文件名（在上传目录中）：").strip()
            upload_file(client_socket, filename)
        elif choice == 3:
            filename = input("请输入要下载的文件名：").strip()
            download_file(client_socket, filename)
        elif choice == 4:
            print("[INFO] 正在断开连接...")
            client_socket.close()
            break
        else:
            print("[ERROR] 无效选项，请重新选择。")

if __name__ == "__main__":
    main()
