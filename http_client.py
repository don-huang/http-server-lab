import socket
import re
import logging
import sys
from urllib.parse import urlparse

# 最大允许的重定向次数，避免无限循环
MAX_REDIRECTS = 10

def fetch_result(url, redirect_count=0, debug=False):
    # 初始化结果字典，用于返回结构化信息
    result = {
        "exit_code": 1,         # 默认失败
        "status_code": None,    # HTTP 状态码
        "content": "",          # HTML 内容
        "error_msg": ""         # 错误信息
    }

    breakpoint()

    # 超过最大跳转次数则失败
    if redirect_count >= MAX_REDIRECTS:
        result["error_msg"] = "Too many redirects"
        return result

    # 仅支持 http://，不支持 https://
    if not url.startswith("http://"):
        result["error_msg"] = "Only http:// URLs are supported"
        return result

    # 解析 URL，提取主机名、端口、路径等
    parsed = urlparse(url)
    host = parsed.hostname
    port = parsed.port if parsed.port else 80
    path = parsed.path if parsed.path else "/"
    if parsed.query:
        path += '?' + parsed.query

    # ⚠️ 动态构造 Host header 字符串（如果不是 80，就加上端口）
    host_header = f"{host}:{port}" if port != 80 else host

    # 建立 socket 连接并发送 HTTP 请求
    try:
        if debug:
            logging.debug(f"Connecting to {host}:{port}")
        with socket.create_connection((host, port)) as s:
            request = f"GET {path} HTTP/1.0\r\nHost: {host_header}\r\n\r\n"
            if debug:
                logging.debug(f"Sending request:\n{request}")
            s.sendall(request.encode())

            # 读取响应直到服务器关闭连接（无 Content-Length）
            response = b""
            while True:
                chunk = s.recv(4096)
                if not chunk:
                    break
                response += chunk
    except Exception as e:
        result["error_msg"] = f"Connection failed: {e}"
        return result

    # 尝试解析响应头和正文
    try:
        header_data, body = response.split(b"\r\n\r\n", 1)
        headers = header_data.decode().split("\r\n")
        status_line = headers[0]

        match = re.match(r"HTTP/\d\.\d (\d+)", status_line)
        status_code = int(match.group(1)) if match else 0
        result["status_code"] = status_code

        # 转换响应头为字典
        header_dict = {}
        for h in headers[1:]:
            if ':' in h:
                k, v = h.split(":", 1)
                header_dict[k.strip().lower()] = v.strip()

        # 处理 301/302 重定向
        if status_code in (301, 302):
            location = header_dict.get("location")
            if location:
                if location.startswith("https://"):
                    result["error_msg"] = f"Redirected to HTTPS not supported: {location}"
                    return result
                if debug:
                    logging.warning(f"Redirected to: {location}")
                return fetch_result(location, redirect_count + 1, debug)
            else:
                result["error_msg"] = "Redirect with no Location header"
                return result

        # 错误状态码仍输出正文，但 exit_code = 1
        if status_code >= 400:
            result["content"] = body.decode(errors="replace")
            return result

        # 仅支持 text/html 内容
        content_type = header_dict.get("content-type", "")
        if not content_type.startswith("text/html"):
            result["error_msg"] = "Unsupported content-type"
            return result

        # 一切成功：记录内容并设 exit_code 为 0
        result["content"] = body.decode(errors="replace")
        result["exit_code"] = 0
        return result

    except Exception as e:
        result["error_msg"] = f"Failed to parse response: {e}"
        return result

# 支持命令行调用，供测试或评分系统使用
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="HTTP/1.0 command-line client using sockets only")
    parser.add_argument("url", help="http:// URL to fetch")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    args = parser.parse_args()

    # 启用 debug 日志（可选）
    if args.debug:
        logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s')
    else:
        logging.basicConfig(level=logging.ERROR)

    # 调用 fetch_result 并处理输出与退出码
    result = fetch_result(args.url, debug=args.debug)
    if result["content"]:
        print(result["content"])
    if result["error_msg"]:
        print(result["error_msg"], file=sys.stderr)
    sys.exit(result["exit_code"])
