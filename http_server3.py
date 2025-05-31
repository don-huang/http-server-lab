import socket
import sys
import json
from urllib.parse import urlparse, parse_qs

def handle_product_request(query):
    try:
        params = parse_qs(query)
        operands = []
        for values in params.values():
            for v in values:
                try:
                    operands.append(float(v))
                except ValueError:
                    return 400, "Bad Request", "application/json", json.dumps({"error": "Invalid operand"})

        if not operands:
            return 400, "Bad Request", "application/json", json.dumps({"error": "No operands"})

        result = 1
        for x in operands:
            result *= x
        if result == float('inf'):
            result = "inf"
        elif result == float('-inf'):
            result = "-inf"

        response_body = json.dumps({
            "operation": "product",
            "operands": operands,
            "result": result
        })
        return 200, "OK", "application/json", response_body
    except Exception as e:
        return 500, "Internal Server Error", "text/plain", str(e)

def run_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("", port))
        s.listen(5)
        print(f"[*] Listening on port {port}...")

        while True:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024).decode()
                if not data:
                    continue
                request_line = data.splitlines()[0]
                method, path, _ = request_line.split()

                parsed = urlparse(path)
                if parsed.path != "/product":
                    status, msg, ctype, body = 404, "Not Found", "text/plain", "404 Not Found"
                else:
                    status, msg, ctype, body = handle_product_request(parsed.query)

                response = f"HTTP/1.0 {status} {msg}\r\nContent-Type: {ctype}\r\n\r\n{body}"
                conn.sendall(response.encode())

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)