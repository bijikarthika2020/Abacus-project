from pymongo import MongoClient
client = MongoClient('mongodb://localhost:27017/')
db = client['tinybeads_db']
students = db['students']
students.insert_one({'name': 'Test Student', 'age': 10})
