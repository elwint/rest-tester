import model
import crypt
from db import session

session.add(model.User(name='Bassie', password=crypt.hash('abc')))
session.add(model.User(name='Tester', password=crypt.hash('def')))
session.add(model.Token(user_id=1, token="test"))

session.add(model.Test(data={
	"id": 1,
	"version": 1,
	"user_id": 1,
	"name": "Test 1",
	"last": {
		"ok": True,
		"status": 200,
		"elapsed_time": 16,
		"timestamp": 1496836918
	},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {
		"method": "GET",
		"url": "http://example.com/tests/1",
		"status": "200",
		"checks": [
			{
				"type": "json",
				"key": "id",
				"compare": "equals",
				"value": "1"
			},
			{
				"type": "json",
				"key": "title",
				"compare": "exists"
			}
		],
		"extract": [
			{
				"type": "json",
				"key": "id",
				"variable": "first_test_id"
			}
		]
	}
}))
session.add(model.Test(data={
	"id": 2,
	"version": 1,
	"user_id": 2,
	"name": "Test 2",
	"last": {},
	"shared_with": [1],
	"autorun": "every_day",
	"group": None,
	"data": {
		"method": "POST",
		"url": "http://example.com/tests/",
		"status": "201",
		"body": "{\"test\": \"test\"}",
		"checks": [
			{
				"type": "json",
				"key": "name",
				"compare": "equals",
				"value": "name"
			},
			{
				"type": "json",
				"key": "id",
				"compare": "equals",
				"value": "first_test_id"
			}
		]
	}
}))
session.add(model.Test(data={
	"id": 3,
	"version": 1,
	"user_id": 1,
	"name": "Test 3",
	"last": {
		"ok": False,
		"status": 200,
		"elapsed_time": 85,
		"timestamp": 1496836920
	},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {
		"method": "GET",
		"url": "http://example.com/1",
		"status": "200"
	}
}))
session.add(model.Test(data={
	"id": 4,
	"version": 2,
	"user_id": 1,
	"name": "Test 4",
	"last": {},
	"shared_with": [],
	"autorun": "never",
	"group": None,
	"data": {
		"method": "GET",
		"url": "http://example.com/1",
		"status": "200"
	}
}))
session.add(model.History(data={
	"test_id": 1,
	"version": 1,
	"ok": True,
	"status": 500,
	"elapsed_time": 337,
	"timestamp": 1496836917
}))
session.add(model.History(data={
	"test_id": 1,
	"version": 1,
	"ok": True,
	"status": 200,
	"elapsed_time": 16,
	"timestamp": 1496836918
}))
session.flush()
