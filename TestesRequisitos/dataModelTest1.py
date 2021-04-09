from cassandra.cluster import Cluster

# Ligação ao cluster, neste caso um cluster de testes local que criei previamente

cluster = Cluster()
session = cluster.connect('pitest')

json = {"sensorId": "0002",
        "timeStamp": "2020-06-01 10:10:10",
        "temperature": "10"}

# É criada uma tabela de tabelas (metadata), uma tabela por cada grupo de atributos de json e tabelas secundárias dos valores de cada um
# pK é o parametro que identifica este registo em especifico e é passado pela API
# Neste caso teremos a table1 com pK = UUID1, sensorId = 0001, timeStamp = 2020-06-01 10:10:10 e temperature = 10
# table1_sensorId com table = table1_sensorId pK = UUID1 e sensorId = 0001
# table1_timeStamp com table = table1_timeStamp pK = UUID1  e timeStamp = 2020-06-01 10:10:10
# table1_temperature com table = table1_temperature pK = UUID1 e temperature = 10


# Mais jsons para testar querying e inserção de dados
json2 = {"sensorId": "0001",
         "timeStamp": "2020-06-01 10:10:10",
         "temperature": "12"}

json3 = {"sensorId": "0002",
         "timeStamp": "2020-06-02 10:10:10",
         "temperature": "12"}

json4 = {"sensorId": "0003",
         "temperature": "12"}


def init():  # Verificar se a tabela de metadados já existe e se não existir criar
    try:
        session.execute("create table metadata (tableName text, sensorId text, tableAtributes list<text>, PRIMARY KEY(tableName) )")
        session.execute("create table sensors (sensor_id text,users text ,tables list<text>, PRIMARY KEY(sensor_id, users) )")
    except:
        pass


# Função para verificar se já existe uma tabela na qual o json possa ser inserido
def checkTable(flatJson, sensor_id):
    lowerParList = []  # Criar uma lista com todos os parametros do flat json em minisculas => Porque o cassandra vai ter as colunas em miniscula
    for par in flatJson.keys():
        lowerParList.append(par.lower())

    lowerParList.append('pk')  # Adicionar pk porque estará em todas as tabelas
    lowerParList.append('sensorId')  # Adicionar pk porque estará em todas as tabelas


    tableAts = session.execute("SELECT * FROM metadata")  # Verifiar os dados da tabela de metadados

    for row in tableAts:
        if set(row[2]) == set(lowerParList) and row[1] == sensor_id:  # Se existir alguma tabela que já possua a mesma formatação retornar o seu nome
            return row[0]
    return None  # Caso contrário retorna None


# Função para criar tabelas
def createTables(flatJson, pk_id, sensor_id):
    sensor_id = str(sensor_id)
    table_name = "table" + str(pk_id)  # Gerar nome da tabela principal // Não sei se este será a forma como vamos gerar nomes // Solução provisória

    strCommand = "create table " + table_name + "(pk text"  # Começar a string de comando que cria a tabela principal
    lowerParList = []  # Lista de parametros / Para colocar na tabela de metadados

    for key in flatJson.keys():  # Para cada chave do flatJson
        key = key.lower()
        lowerParList.append(key)  # Recolher os parametros para a tabela de metadados
        strCommand = strCommand + ", " + key + " text"  # Adicionar à string do comando que cria a tabela principal
        session.execute(
            "create table " + table_name + "_" + key + " (tableName text, pk text," + key + " text, PRIMARY KEY( tableName, " + key + ", pk))")  # Criar a tabela secundária correspondente a essa chave

    lowerParList.append('pk')
    strCommand = strCommand + ", PRIMARY KEY(pk)) "  # Acabar a string de comando após todos os parametros serem adicionados e correr o comando
    session.execute(strCommand)

    session.execute("insert into metadata(tableName, sensorId, tableAtributes) values ('" + table_name + "', '" + sensor_id + "', " + str(lowerParList) + ")")  # Adicionar a a tabela principal à tabela de metadados
    return table_name  # retorna o table_name da tabela principal criada


# Função de inserção de um json
def insertInto(flatJson, pk_id, sensor_id):  # os parametros são o json e a pk que será passada pela API

    pk_id = str(pk_id)
    table_name = checkTable(flatJson, sensor_id)  # Verificar se existe uma tabela em que os dados possam ser inseridos
    print("after checkTable(), table name: " + str(table_name))
    new_table_name = table_name
    if not table_name:
        table_name = createTables(flatJson,pk_id, sensor_id)  # Caso não exista chamar a função que cria que retorna o seu nome (da principal)

    strInsert = "insert into " + table_name + "(pK"  # strInsert é a string de instrução / O que escreveriamos se estivessemos a inserir por terminal

    for key in flatJson.keys():
        strInsert = strInsert + ", " + key

    strInsert = strInsert + ") values('" + pk_id + "'"  # Acabar os campos da tabela e começar a inserir os valores na string

    for key in flatJson.keys():  # Ciclo para adicionar os valores à string de instrução
        strInsert = strInsert + ", '" + flatJson[key] + "'"

    strInsert = strInsert + ")"  # Fechar a string

    print(strInsert)  # Print e executar o comando
    session.execute(strInsert)

    insertSecondaryTables(table_name, flatJson,
                          pk_id)  # Inserir os dados nas tabelas adicionais para se poder fazer querying complexo
    return new_table_name


# Função de inserção nas tabelas secundárias
def insertSecondaryTables(table, flatJson, pk):
    for key in flatJson.keys():  # Para cada parametro do flatJson adicionar a informação às tabelas adicionais
        insertStr = "insert into " + table + "_" + key + " (tableName, pK, " + key + ") values('" + table + "','" + pk + "', '" + \
                    flatJson[key] + "')"
        session.execute(insertStr)


def insertIntoSensor(flatJson,pk_id, sensor_id, user):
    sensor_id = str(sensor_id)
    new_table_name = insertInto(flatJson, pk_id, sensor_id)
    sensor = session.execute("SELECT * FROM sensors where sensor_id = '" + sensor_id + "'")
    if not sensor:
        if new_table_name is not None:
            session.execute("insert into sensors (sensor_id, users, tables) values ('" + sensor_id + "', '" + user + "', '" + new_table_name + "') ")  # Adicionar a a tabela principal à tabela de metadados
    else:
        tables = sensor.tables
        if new_table_name is not None:
            tables.append(new_table_name)
            session.execute("update sensors set tables = '" + tables + "' where sensor_id = '" + sensor_id + "'")


def subQuery(table, param, condition):
    retList = []  # Lista de pks a retornar
    condition = condition[0] + "'" + condition[1:len(
        condition)] + "'"  # Alterar a formatação da condição para ser compativel com cql

    pkRows = session.execute(
        "Select pk from " + table + "_" + param + " where tableName= '" + table + "' and " + param + condition)  # Executar a query secundária
    # print("Select pk from " + table + "_" + param + " where tableName= '" + table + "' and " + param + condition)

    for row in pkRows:  # Para cada pk retornado adicionar a lista de retorno
        retList.append(row[0])

    return retList


# Função de querying geral
def query(table, projList, paramConditionDictionary):
    pkLists = []  # Lista de listas de pks validadados pelas subqueries

    strCommand = "select "  # Adicionar ao comando os parametros que desejamos procurar
    for par in projList:
        strCommand = strCommand + par
        if not projList[len(projList) - 1] == par:
            strCommand = strCommand + ','

    strCommand = strCommand + ' from ' + table + ' where '  # Adicionar ao comando a tabela principal em que desejamos procurar
    # print(strCommand)

    for key in paramConditionDictionary:  # Para cada conjunto de parametro e condição pelos quais queremos filtrar fazer uma subquery nas tabelas secundárias
        value = paramConditionDictionary[key]
        pkLists.append(
            subQuery(table, key, value))  # Adicionar a lista de resultados dessas subqueries à lista de listas das pks

    # print(pkLists)

    pks = set(pkLists[0]).intersection(
        *pkLists)  # Fazer a interceção de todas as listas para verificar que parametros correspondem a todas as filtragens
    # print(pks)

    for pk in pks:  # Pesquisar na tabela principal e apresentar os resultados
        finalCommand = strCommand + "pk='" + pk + "'"
        # print(finalCommand)
        rows = session.execute(finalCommand)
        for row in rows:
            print(str(row)[4:len(str(row)) - 1])
            print("..........................................")


init()

print("\n")

print("Inserts")
insertIntoSensor(json, 1, 2, "Marta")
insertIntoSensor(json2, 2, 1, "Luis")
insertIntoSensor(json3, 3, 2, "Marta")
insertIntoSensor(json4, 4, 3, "Luis")

print("\n")

print(
    "Query #1 Procurar na tabela do primeiro tipo de formatação quando é que o sensor com id 0002 registou temperaturas superiores a 11 graus")
print("Results:")
query('table1', ['timestamp'], {'temperature': '>11', 'sensorid': '=0002'})

print("\n")

print("Query #2 Procurar na tabela do primeiro tipo de formatação todos os registos com temperatura = 12")
print("Results:")
query('table1', ['*'], {'temperature': '=12'})
