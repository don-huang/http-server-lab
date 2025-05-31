# 🧪 CS340 HTTP Project (Socket Programming in Python)

This repository contains an educational implementation of a simplified HTTP/1.0 stack using raw sockets in Python, developed as part of the [CS340: Intro to Computer Networking](https://stevetarzia.com/teaching/340/) course at Northwestern University.

## 📦 Contents

| File | Description |
|------|-------------|
| `http_client.py` | Simplified curl-like HTTP client using raw sockets |
| `http_server1.py` | Basic HTTP server (single connection) |
| `http_server2.py` | Multi-client HTTP server using `select` |
| `http_server3.py` | Dynamic JSON API server supporting multiplication |
| `rfc2616.html` | Static file used for server response tests |
| `http_server2_test.ipynb` | Jupyter notebook testing multi-client behavior |
| `http_server3_test.ipynb` | Jupyter notebook testing dynamic multiplication API |
| `test_server3.py` | Script to test `http_server3` via `requests.get` |
| `Http Server Debug Notebook multi-clients.ipynb` | Debug session notebook for server2 |
| `Http Client Tests.ipynb` | Client-level test and validation notebook |

## 🧪 Testing

### Part 1 – HTTP Client
```bash
python3 http_client.py http://insecure.stevetarzia.com/basic.html
```

### Part 2 – Single-Connection Server
```bash
python3 http_server1.py 8011
curl http://192.168.50.253:8011/rfc2616.html
```

### Part 3 – Multi-Connection Server
```bash
python3 http_server2.py 8011
telnet 192.168.50.253 8011
curl http://192.168.50.253:8011/rfc2616.html
```

### Part 4 – Dynamic JSON Server
```bash
python3 http_server3.py 8011
curl "http://192.168.50.253:8011/product?a=2&b=3"
```

## ✅ Example Part 4 API Calls (Port `8011`, Host `192.168.50.253`)

```bash
curl "http://192.168.50.253:8011/product?a=12&b=60&another=0.5"     # ✅ 200 OK
curl "http://192.168.50.253:8011/product"                            # ❌ 400 Bad Request (No operands)
curl "http://192.168.50.253:8011/product?a=foo"                      # ❌ 400 Bad Request (Invalid operand)
curl "http://192.168.50.253:8011/wrongpath?a=1"                      # ❌ 404 Not Found
curl "http://192.168.50.253:8011/product?a=1e308&b=1e10"             # ⚠️ 200 OK (Result = "inf")
```

## 📚 References

- [RFC 2616 - HTTP/1.1](https://www.rfc-editor.org/rfc/rfc2616.html)
- Python built-in modules: [`socket`](https://docs.python.org/3/library/socket.html), [`select`](https://docs.python.org/3/library/select.html), [`json`](https://docs.python.org/3/library/json.html)

## ⚠️ Disclaimer

This project is for **educational purposes only** and is not intended for production use. It omits many security and efficiency features of real HTTP servers (e.g., HTTPS, MIME type handling, thread pooling).
