import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
session.add(model.Token(user_id=1, token="test"))

session.add(model.Test(data={
	"id": 0,
	"user_id": 1,
	"name": "Test 1",
	"last": {
		"ok": None,
		"time": None
	},
	"shared_with": [],
	"autorun_time": -1,
	"group": None,
	"data": {}
}))
session.add(model.Test(data={
	"id": 1,
	"user_id": 0,
	"name": "Test 2",
	"last": {
		"ok": None,
		"time": None
	},
	"shared_with": [1],
	"autorun_time": -1,
	"group": None,
	"data": {}
}))
session.add(model.History(data={
	"test_id": 0,
	"ok": False,
	"time": 1496836917
}))
session.add(model.History(data={
	"test_id": 0,
	"ok": True,
	"time": 1496836918
}))
session.flush()
