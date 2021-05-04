# Django-RestAPI-Cassandra
Django Rest API using Cassandra

## install requirements and create database

### Usar PRIMARY KEY(sensor_id) para estar de acordo com os models.py

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

python3 manage.py sync_cassandra

python manage.py runserver

```

### notas

$ python3 manage.py sync_cassandra é outra forma de criar o keyspace

vai buscar ao settings.py a db que está la definida na linha 87

### urls

http://127.0.0.1:8000/sensors/detail/0001/

http://127.0.0.1:8000/sensors/list/

http://127.0.0.1:8000/sensors/create/

# Grafana

### Comandos básicos grafana (iniciar e parar servidor)

```bash
$ service grafana-server {start|stop|restart|force-reload|status}
```

### Comandos que fiz antes de poder meter o server a correr (não sei quais são precisos refazer)
```bash
$ wget https://dl.grafana.com/oss/release/grafana_7.5.5_amd64.deb

$ sudo apt-get install -y adduser libfontconfig1

$ sudo dpkg -i grafana_7.5.5_amd64.deb

$ sudo systemctl status grafana-server

$ sudo enable grafana-server
```

### Install JSON API Grafana Datasource

```bash
sudo grafana-cli plugins install simpod-json-datasource
```