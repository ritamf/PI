# Django-RestAPI-Cassandra
Django Rest API using Cassandra

## install requirements and create database

```bash
pip install requirements.txt

sudo service cassandra start 

cqlsh

CREATE KEYSPACE "db" WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 3};

CREATE TABLE db.products (id UUID PRIMARY KEY. attributes Map<Text,Text>);

exit

```

```bash
source bin/activate

python manage.py runserver