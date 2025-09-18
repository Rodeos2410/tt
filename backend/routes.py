
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from models import User, UserCreate, UserLogin, Product, ProductCreate
from models import Purchase
from typing import List
from db import get_session, init_db
from sqlmodel import select
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta


router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "CHANGE_ME_TO_SECURE_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(authorization: str | None = Header(None), session=Depends(get_session)):
    # Получаем токен из заголовка Authorization: Bearer <token>
    token = None
    if authorization and authorization.startswith('Bearer '):
        token = authorization.split(' ', 1)[1]
    if not token:
        raise HTTPException(status_code=401, detail='Не аутентифицирован')
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload.get('sub'))
    except JWTError:
        raise HTTPException(status_code=401, detail='Неверный токен')
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    if not user:
        raise HTTPException(status_code=401, detail='Пользователь не найден')
    if getattr(user, 'blocked', False):
        raise HTTPException(status_code=403, detail='Пользователь заблокирован')
    return user

@router.get('/me/balance')
def get_balance(current_user: User = Depends(get_current_user)):
    return {"balance": current_user.balance}

@router.post('/me/deposit')
def deposit_balance(amount: float, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Сумма должна быть положительной")
    current_user.balance += amount
    session.add(current_user)
    session.commit()
    return {"balance": current_user.balance}



@router.post('/register')
def register(user: UserCreate, session=Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    existing = session.exec(statement).first()
    if existing:
        raise HTTPException(status_code=400, detail="Пользователь уже существует")
    db_user = User(username=user.username, email=user.email, hashed_password=get_password_hash(user.password))
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return {"id": db_user.id, "username": db_user.username, "email": db_user.email}


@router.post('/login')
def login(user: UserLogin, session=Depends(get_session)):
    statement = select(User).where(User.email == user.email)
    db_user = session.exec(statement).first()
    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")
    access_token = create_access_token({"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer", "user_id": db_user.id}


@router.post('/products', response_model=Product)
def add_product(product: ProductCreate, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    db_product = Product(title=product.title, description=product.description, price=product.price, owner_id=current_user.id if current_user else None, file_url=product.file_url)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)
    return db_product


@router.post('/purchase/bulk')
def purchase_bulk(items: List[dict], current_user: User = Depends(get_current_user), session=Depends(get_session)):
    """Оформить несколько покупок за раз. items: [{"product_id":int, "qty":int}, ...]"""
    results = []
    grand_total = 0.0
    for it in items:
        pid = int(it.get('product_id')) if it.get('product_id') is not None else None
        qty = int(it.get('qty') or 1)
        if not pid:
            continue
        statement = select(Product).where(Product.id == pid)
        p = session.exec(statement).first()
        if not p:
            continue
        total = p.price * qty
        grand_total += total
    if current_user.balance < grand_total:
        raise HTTPException(status_code=400, detail=f"Недостаточно средств. Требуется {grand_total} ₽, ваш баланс: {current_user.balance} ₽")
    # списываем средства и записываем покупки
    for it in items:
        pid = int(it.get('product_id')) if it.get('product_id') is not None else None
        qty = int(it.get('qty') or 1)
        if not pid:
            continue
        statement = select(Product).where(Product.id == pid)
        p = session.exec(statement).first()
        if not p:
            continue
        total = p.price * qty
        purchase = Purchase(buyer_id=current_user.id, product_id=pid, qty=qty, total_price=total)
        session.add(purchase)
        session.commit()
        session.refresh(purchase)
        results.append({"purchase_id": purchase.id, "product_id": pid})
    current_user.balance -= grand_total
    session.add(current_user)
    session.commit()
    return {"message": "Покупки оформлены", "results": results, "balance": current_user.balance}


@router.get('/products', response_model=List[Product])
def get_products(session=Depends(get_session)):
    statement = select(Product)
    return session.exec(statement).all()


@router.get('/products/{product_id}', response_model=Product)
def get_product(product_id: int, session=Depends(get_session)):
    statement = select(Product).where(Product.id == product_id)
    p = session.exec(statement).first()
    if not p:
        raise HTTPException(status_code=404, detail='Товар не найден')
    return p


@router.get('/purchases')
def get_my_purchases(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    statement = select(Purchase).where(Purchase.buyer_id == current_user.id)
    return session.exec(statement).all()


@router.get('/admin/users')
def admin_list_users(current_user: User = Depends(get_current_user), session=Depends(get_session)):
    # allow only admin by hardcoded check for now
    if current_user.email != 'admin@nexusdark.ru':
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    statement = select(User)
    return session.exec(statement).all()


@router.post('/admin/users/{user_id}/block')
def admin_block_user(user_id: int, current_user: User = Depends(get_current_user), session=Depends(get_session)):
    if current_user.email != 'admin@nexusdark.ru':
        raise HTTPException(status_code=403, detail='Доступ запрещён')
    statement = select(User).where(User.id == user_id)
    u = session.exec(statement).first()
    if not u:
        raise HTTPException(status_code=404, detail='User not found')
    u.blocked = True
    session.add(u)
    session.commit()
    return {"message": "User blocked"}
