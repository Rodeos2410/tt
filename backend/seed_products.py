from sqlmodel import Session, create_engine, select, SQLModel
import importlib.util
import sys
import os

# load backend.models module from file
spec = importlib.util.spec_from_file_location('backend.models', os.path.join(os.path.dirname(__file__), 'models.py'))
mod = importlib.util.module_from_spec(spec)
sys.modules['backend.models'] = mod
spec.loader.exec_module(mod)
Product = mod.Product
User = getattr(mod, 'User', None)
import os

sqlite_file_name = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=False)

if __name__ == '__main__':
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        statement = select(Product)
        existing = session.exec(statement).all()
        if existing:
            print('Products already present:', len(existing))
        else:
            # find an existing user to assign as owner (prefer admin)
            owner_id = None
            if User is not None:
                stmt = select(User).where(getattr(User, 'email') == 'admin@nexusdark.ru')
                admin = session.exec(stmt).first()
                if admin:
                    owner_id = admin.id
                else:
                    # find any user
                    any_user = session.exec(select(User)).first()
                    if any_user:
                        owner_id = any_user.id
                    else:
                        # create a lightweight user
                        try:
                            u = User(username='seeduser', email='seed@local', hashed_password='seed')
                            session.add(u)
                            session.commit()
                            session.refresh(u)
                            owner_id = u.id
                        except Exception as e:
                            print('Failed to create seed user:', e)
            # prepare products with valid owner_id
            samples = [
                Product(title='Фруктовый чай', description='Ароматный чай с фруктами', price=199.0, owner_id=owner_id, file_url='https://avatars.mds.yandex.net/i?id=d68741f8aa1bc71825f9ee1a3d07702b32833e16-11380463-images-thumbs&n=13'),
                Product(title='Органический мёд', description='Натуральный мёд', price=349.0, owner_id=owner_id, file_url='https://avatars.mds.yandex.net/i?id=144af57b4fcd988a8a3462b2c75ce9fc551d83c2-5694385-images-thumbs&n=13'),
                Product(title='Свежие яблоки', description='Сочные яблоки', price=89.0, owner_id=owner_id, file_url='https://avatars.mds.yandex.net/i?id=6e4d70075d3c1e54fc7c8ceb30b27626ba0ccd7e-5658951-images-thumbs&n=13'),
                Product(title='Клубника', description='Сладкая клубника', price=499.0, owner_id=owner_id, file_url='https://cdn1.youla.io/files/images/780_780/68/51/685176c67a06fa25b00fe576-2.jpg'),
            ]
            for p in samples:
                session.add(p)
            session.commit()
            print('Seeded products')
