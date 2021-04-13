# Django-RestAPI-Cassandra
Django Rest API using Cassandra

## install requirements and create database

```bash
pip install requirements.txt

sudo service cassandra start 

cqlsh

CREATE KEYSPACE "db" WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};

create table db.sensors (sensor_id text,user text ,tables list<text>, pks list<text>, PRIMARY KEY(user, sensor_id) );

insert into db.sensors (sensor_id, user, tables, pks) VALUES ('0001', 'joao', ['table1', 'table2'], ['1','2']);

insert into db.sensors (sensor_id, user, tables, pks) VALUES ('0002', 'rita', ['table13', 'table4'], ['1','2']);

insert into db.sensors (sensor_id, user, tables, pks) VALUES ('0003', 'luis', ['table23', 'table14'], ['1','2','3']);

insert into db.sensors (sensor_id, user, tables, pks) VALUES ('0004', 'goncalo', ['table2', 'table4'], ['5','2','3']);

insert into db.sensors (sensor_id, user, tables, pks) VALUES ('0005', 'marta', ['table3', 'table4'], ['4','2','3','50']);

exit

```

```bash
source bin/activate

python manage.py runserver

```

http://127.0.0.1:8000/sensors/detail/0001/

http://127.0.0.1:8000/sensors/list/

http://127.0.0.1:8000/sensors/create/