import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
session.add(model.Test(user_id=1, name='test1', last_ok=True, data='data'))
session.add(model.Test(user_id=1, name='test2', last_ok=False, data='data'))
session.add(model.Test(user_id=1, name='test3', last_ok=False, data='data'))
session.add(model.Test(user_id=1, name='test4', last_ok=True, data='data'))
session.add(model.Test(user_id=2, name='test1', last_ok=True, data='data'))
session.add(model.Test(user_id=2, name='test2', last_ok=True, data='data'))
