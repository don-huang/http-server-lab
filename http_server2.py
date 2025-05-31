# http_server2.py
# 多连接 HTTP Server，基于 select 实现非阻塞 I/O，适用于 Jupyter 环境

import socket        # 用于网络通信
import os            # 用于访问文件系统
import select        # 用于多路复用 I/O

# === 常量定义 ===
BUFFER_SIZE = 4096
SUPPORTED_SUFFIXES = (".html", ".htm")  # 支持的文件后缀，仅允许访问这些类型

# === 生成 HTTP 响应头部 ===
def generate_headers(status_code, content_length=0, content_type="text/html"):
    reason = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found"
    }.get(status_code, "Internal Server Error")  # 根据状态码设置响应原因

    headers = [
        f"HTTP/1.0 {status_code} {reason}",
        f"Content-Length: {content_length}",   # 内容长度（字节）
        f"Content-Type: {content_type}",       # 内容类型
        "Connection: close",                   # 告诉浏览器连接会被关闭
        ""
    ]
    return "\r\n".join(headers) + "\r\n"  # 返回完整 header 字符串

# === 解析 HTTP 请求，提取 GET 的文件路径 ===
def parse_request(data):
    try:
        line = data.split("\r\n")[0]          # 获取第一行：GET /xxx.html HTTP/1.0
        method, path, _ = line.split(" ")     # 拆解 method、path 和协议版本
        if method != "GET":
            return None                       # 只允许 GET 方法
        return path.lstrip("/")               # 去除路径前导 "/"
    except:
        return None                           # 格式错误直接返回 None

# === 主函数：运行多连接 HTTP 服务器 ===
def run_server_select(port):
    # 1. 创建 TCP socket 并绑定端口
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # 允许端口复用
    server_socket.bind(("", port))      # 监听任意 IP（本机）
    server_socket.listen(10)            # 设置最大连接 backlog
    print(f"[*] Listening on port {port}...")

    open_connections = []  # 当前活动连接的 socket 列表

    # 2. 主循环
    while True:
        read_list = open_connections + [server_socket]  # select 的监听列表
        readable, _, _ = select.select(read_list, [], [])  # 只监听读事件

        for sock in readable:
            # 3.a 如果是服务器 socket 可读，说明有新连接
            if sock is server_socket:
                conn, addr = server_socket.accept()
                print(f"[+] Accepted connection from {addr}")
                open_connections.append(conn)  # 添加到连接列表

            # 3.b 如果是已有连接的 socket 可读，表示有请求数据到达
            else:
                try:
                    data = sock.recv(BUFFER_SIZE).decode("utf-8")  # 读取请求数据
                    if not data:
                        open_connections.remove(sock)
                        sock.close()
                        continue  # 客户端断开

                    print("[DEBUG] Raw Request:\n", data)
                    filename = parse_request(data)  # 提取请求的文件路径

                    # 4. 无效请求或非 GET 方法
                    if not filename:
                        response = generate_headers(403) + "<h1>403 Forbidden</h1>"
                        sock.sendall(response.encode())
                        open_connections.remove(sock)
                        sock.close()
                        continue

                    # 5. 文件不存在
                    if not os.path.isfile(filename):
                        response = generate_headers(404) + "<h1>404 Not Found</h1>"
                        sock.sendall(response.encode())
                        open_connections.remove(sock)
                        sock.close()
                        continue

                    # 6. 文件类型受限
                    if not filename.endswith(SUPPORTED_SUFFIXES):
                        response = generate_headers(403) + "<h1>403 Forbidden</h1>"
                        sock.sendall(response.encode())
                        open_connections.remove(sock)
                        sock.close()
                        continue

                    # 7. 正常读取文件并返回内容
                    with open(filename, "rb") as f:
                        body = f.read()
                        headers = generate_headers(200, len(body))
                        sock.sendall(headers.encode() + body)

                except Exception as e:
                    print(f"[!] Error: {e}")
                    sock.sendall(b"HTTP/1.0 500 Internal Server Error\r\n\r\n")

                finally:
                    if sock in open_connections:
                        open_connections.remove(sock)
                    sock.close()  # 每次请求处理后关闭连接（非 keep-alive）

# === 脚本直接运行时启动服务器（适用于 CLI 环境）===
if __name__ == "__main__":
    run_server_select(8011)
