import socket
import sys
import os

# 每次读取数据块大小
BUFFER_SIZE = 4096
# 仅允许的 HTML 文件扩展名
SUPPORTED_SUFFIXES = (".html", ".htm")

# 构造 HTTP 响应头部
def generate_headers(status_code, content_length=0, content_type="text/html"):
    reason = {
        200: "OK",
        403: "Forbidden",
        404: "Not Found"
    }.get(status_code, "Internal Server Error")

    headers = [
        f"HTTP/1.0 {status_code} {reason}",
        f"Content-Length: {content_length}",
        f"Content-Type: {content_type}",
        "Connection: close",
        ""
    ]
    return "\r\n".join(headers) + "\r\n"

# 从 HTTP 请求中解析出请求的文件名
def parse_request(request_data):
    try:
        line = request_data.split("\r\n")[0]
        method, path, _ = line.split(" ")
        if method != "GET":
            return None
        return path.lstrip("/")
    except Exception:
        return None

# 启动调试模式的服务器函数，支持多连接处理
def run_server_debug(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # ✅ 添加端口重用，避免 TIME_WAIT 状态影响
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(("", port))
        server_socket.listen(2)
        print(f"[*] Debug mode: listening on port {port}...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"[+] Connection from {addr}")
                try:
                    request = conn.recv(BUFFER_SIZE).decode("utf-8")
                    print("[DEBUG] Raw Request:\n", request)

                    filename = parse_request(request)

                    if not filename:
                        response = generate_headers(403) + "<h1>403 Forbidden</h1>"
                        conn.sendall(response.encode())
                        continue

                    if not os.path.isfile(filename):
                        response = generate_headers(404) + "<h1>404 Not Found</h1>"
                        conn.sendall(response.encode())
                        continue

                    if not filename.endswith(SUPPORTED_SUFFIXES):
                        response = generate_headers(403) + "<h1>403 Forbidden</h1>"
                        conn.sendall(response.encode())
                        continue

                    with open(filename, "rb") as f:
                        body = f.read()
                        headers = generate_headers(200, len(body))
                        conn.sendall(headers.encode() + body)

                except Exception as e:
                    print(f"[!] Error: {e}")
                    conn.sendall(b"HTTP/1.0 500 Internal Server Error\r\n\r\n")

# 主程序入口（调试默认端口为 8011）
if __name__ == "__main__":
    port = 8011
    run_server_debug(port)
