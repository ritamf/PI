# DBoT - Database of Things

A software product which can collect and analyse IoT data.

## Setup and execution of code

1. Install the requirements.

```bash
pip install -r requirements.txt
```

2. Run the code.

```bash
python dataModelTest1.py
```

## Arquitecture

![Arquitecture](./arquitecture/arquitecture.png)

## Data Model

```json
Json1 = {"sensorId" : "0001",
"timeStamp" : "2020-06-01 10:10:10",
"temperature" : "10"}

Json2 = {"sensorId" : "0002",
"timeStamp" : "2020-06-01 10:10:10",
"temperature" : "11"}

Json3 = {"sensorId" : "0001",
"temperature" : "10"}
```

* Metadata(tableName, tableAtributes) PRIMARY KEY(tableName)

'table1' | ['sensorId', 'timeStamp', 'temperature', 'pk']
'table2' | ['sensorId', 'temperature']


* table1(pk, sensorId, timeStamp, temperature) PRIMARY KEY(pk)

    * pk is an uuid automatically generated that might be passed through API Rest

    Uuid1 | 0001 | 2020-06-01 10:10:10 | 10
    Uuid2 | 0002 | 2020-06-01 10:10:10 | 11


* table1_sendorId(tableName, pk, sensorId) PRIMARY KEY(tableName, sensorId)

'table1' | uuid1 | 0001
'table1' | uuid2 | 0002


* table1_timeStamp(tableName, pk, timeStamp) PRIMARY KEY(tableName, timeStamp)

'table1' | uuid | 2020-06-01 10:10:10
'table1' | uuid2 | 2020-06-01 10:10:10


* table1_temperature(tableName, pk, temperature) PRIMARY KEY(tableName, temperature)

'table1' | uuid | 10
'table1' | Uuid2 | 11


* table2(pk, sensorId, temperature) PRIMARY KEY(pk)

Uuid3 | 0001 | 10


* table2_sendorId(tableName, pk, sensorId) PRIMARY KEY(tableName, sensorId)

'table2' | uuid3 | 0001


* table2_temperature(tableName, pk, temperature) PRIMARY KEY(tableName, temperature)

'table2' | Uuid3 | 10
