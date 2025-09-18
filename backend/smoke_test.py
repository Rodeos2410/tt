import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from fastapi.testclient import TestClient
from backend.main import app
from backend.db import init_db, engine
from sqlmodel import Session, select
from backend.models import Product


def run():
    init_db()
    # ensure a product exists
    with Session(engine) as s:
        stmt = select(Product)
        existing = s.exec(stmt).first()
        if not existing:
            p = Product(title='Тестовый товар', description='desc', price=100.0, file_url='https://picsum.photos/seed/test/400/300')
            s.add(p)
            s.commit()
            s.refresh(p)
            print('Created product id=', p.id)
        else:
            print('Found product id=', existing.id)

    client = TestClient(app)

    # List products
    r = client.get('/products')
    print('/products', r.status_code, r.json())

    # Register
    user = {'username': 'smoketest', 'email': 'smoketest@example.com', 'password': 'testing123'}
    r = client.post('/register', json=user)
    print('/register', r.status_code, r.json())

    # Login
    r = client.post('/login', json={'email': user['email'], 'password': user['password']})
    print('/login', r.status_code, r.json())
    if r.status_code != 200:
        print('Login failed, abort')
        return
    token = r.json().get('access_token')
    headers = {'Authorization': 'Bearer ' + token}

    # Deposit 500
    r = client.post('/me/deposit?amount=500', headers=headers)
    print('/me/deposit', r.status_code, r.json())

    # Get products to know id
    r = client.get('/products')
    prods = r.json()
    if not prods:
        print('No products to buy')
        return
    pid = prods[0]['id']

    # Attempt bulk purchase
    items = [{'product_id': pid, 'qty': 1}]
    r = client.post('/purchase/bulk', json=items, headers=headers)
    print('/purchase/bulk', r.status_code, r.text)


if __name__ == '__main__':
    run()
import importlib, json, traceback
from fastapi.testclient import TestClient

try:
    app = importlib.import_module('backend.main').app
    client = TestClient(app)

    def p(name, r):
        try:
            print(name, r.status_code)
            print(json.dumps(r.json(), ensure_ascii=False, indent=2))
        except Exception:
            print(name, r.status_code, r.text)

    r = client.get('/')
    p('ROOT', r)

    r = client.post('/register', json={'username':'tester','email':'tester@example.com','password':'pass123'})
    p('REG', r)

    r = client.post('/login', json={'email':'tester@example.com','password':'pass123'})
    p('LOGIN', r)

    token = r.json().get('access_token') if r.status_code == 200 else None
    headers = {'Authorization': f'Bearer {token}'} if token else {}
    r = client.get('/products', headers=headers)
    p('PRODUCTS', r)

except Exception:
    traceback.print_exc()
