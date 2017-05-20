import bcrypt

import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
