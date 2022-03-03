import pymongo

client = pymongo.MongoClient('mongodb://root:CQhHT8VXr9@localhost:30006/')
db = client
print(db.name)
# 'test'
# >>> db.my_collection
# Collection(Database(MongoClient('localhost', 27017), 'test'), 'my_collection')
# >>> db.my_collection.insert_one({"x": 10}).inserted_id
# ObjectId('4aba15ebe23f6b53b0000000')
# >>> db.my_collection.insert_one({"x": 8}).inserted_id
# ObjectId('4aba160ee23f6b543e000000')
# >>> db.my_collection.insert_one({"x": 11}).inserted_id
# ObjectId('4aba160ee23f6b543e000002')
# >>> db.my_collection.find_one()
# {'x': 10, '_id': ObjectId('4aba15ebe23f6b53b0000000')}