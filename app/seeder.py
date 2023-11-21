from os import environ

from app.extensions import create_session
from app.models.user import User

def seed():
    passwords = environ.get('PASSWORDS').split(', ')
    db_session = create_session()
    admin = User(login="Andrey", status="superuser")
    admin.set_password(passwords[0])
    print(passwords[0])
    db_session.add(admin)
    for i in range(1, 5):
        admin = User(login="admin_"+str(i), status="superuser")
        admin.set_password(passwords[i])
        db_session.add(admin)
    db_session.commit()
    db_session.close()

