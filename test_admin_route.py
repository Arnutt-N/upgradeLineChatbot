#!/usr/bin/env python3
import sys
sys.path.append('.')
from app.main import app
from fastapi.testclient import TestClient

def test_admin_route():
    client = TestClient(app)
    response = client.get('/admin')
    print(f'Status: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    if response.status_code != 200:
        print(f'Error: {response.text}')
    else:
        print('Success: Admin page reachable')
        print(f'Content type: {response.headers.get("content-type")}')
        if response.headers.get("content-type") == "text/html; charset=utf-8":
            print('Response is HTML - template rendered successfully')
        else:
            print('Response is not HTML - template issue')

if __name__ == "__main__":
    test_admin_route()