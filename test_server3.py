import requests

print("✅ Valid request")
r = requests.get("http://localhost:8000/product?a=2&b=3")
print(r.status_code, r.text)

print("\n⚠️ Missing params")
r = requests.get("http://localhost:8000/product")
print(r.status_code, r.text)

print("\n❌ Invalid param")
r = requests.get("http://localhost:8000/product?a=bad")
print(r.status_code, r.text)

print("\n❌ Wrong path")
r = requests.get("http://localhost:8000/wrongpath")
print(r.status_code, r.text)