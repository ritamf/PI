from DBoT.DB import DB
from Parser.JsonParser import JsonParser

DB_Obj = DB('pitest')
Parser_Obj = JsonParser()

flat_j1 = Parser_Obj.read_json('Json_Examples\Json1.json')
flat_j2 = Parser_Obj.read_json('Json_Examples\Json2.json')
flat_j3 = Parser_Obj.read_json('Json_Examples\Json3.json')
flat_j4 = Parser_Obj.read_json('Json_Examples\Json4.json')
flat_j5 = Parser_Obj.read_json('Json_Examples\Json5.json')
flat_j6 = Parser_Obj.read_json('Json_Examples\Json6.json')
flat_j7 = Parser_Obj.read_json('Json_Examples\Json7.json')

DB_Obj.insertIntoSensor(flat_j1, 1, 2, "Marta")
DB_Obj.insertIntoSensor(flat_j2, 2, 1, "Luis")
DB_Obj.insertIntoSensor(flat_j3, 3, 2, "Marta")
DB_Obj.insertIntoSensor(flat_j4, 4, 3, "Luis")
DB_Obj.insertIntoSensor(flat_j5, 5, 1, "Luis")
DB_Obj.insertIntoSensor(flat_j6, 6, 4, "Luis")
DB_Obj.insertIntoSensor(flat_j7, 7, 2, "Marta")

queryResult1 = DB_Obj.query('table1', ['timestamp'], {'temperature': '>11', 'sensorid': '=0002'})
queryResult2 = DB_Obj.queryPerUser('Luis', ['*'], {'sensorid': '=0001'})
queryResult3 = DB_Obj.queryPerSensor('Marta', '2', ['*'], {'temperature': '=12'})

print("\n")
print(queryResult1)
print("\n")
print(queryResult2)
print("\n")
print(queryResult3)