from cassandra.cluster import Cluster

#Ligação ao cluster, neste caso um cluster de testes local que criei previamente
cluster = Cluster()
session = cluster.connect('pitest')


json = {"sensorId" : "0002",
"timeStamp" : "2020-06-01 10:10:10",
"temperature" : "10"}
#Para cada estrutura flatJson como esta, ter uma tabela com cada um dos campos e n outras tables e pk, sendo n o numero de parametros por exemplo 3 neste caso.
#pK é o parametro que identifica este registo em especifico e é composto pelo agregado de todos os parametros para poder ser utilizado agnosticamente
#Neste caso teremos a table1 com pK = 00012020-06-01 10:10:1010, sensorId = 0001, timeStamp = 2020-06-01 10:10:10 e temperature = 10
#table1_sensorId com pK = 00012020-06-01 10:10:1010 e sensorId = 0001
#table1_timeStamp com pK = 00012020-06-01 10:10:1010  e timeStamp = 2020-06-01 10:10:10
#table1_temperature com pK = 00012020-06-01 10:10:1010 e temperature = 10


#Função para verificar se já existe uma tabela na qual o json possa ser inserido
def checkTable(flatJson):
 
    lowerParList = []                          #Criar uma lista com todos os parametros do flat json em minisculas => Porque o cassandra vai ter as colunas em miniscula
    for par in flatJson.keys():
        lowerParList.append(par.lower())
 
    lowerParList.append('pk')                  #Adicionar pk porque estará em todas as tabelas

    tableRows = session.execute("select table_name from system_schema.tables where keyspace_name = 'pitest'")  #Obter o nome das tabelas existentes na base de dados
    tables = []
    
    for row in tableRows:                         #Retirar as tabelas secundárias e obter apenas o nome
        if '_' not in row.table_name:
            tables.append(row.table_name)

    for table in tables:                          #Para cada tabela, verificar o nome das colunas 
        columns = []
        columnRows = session.execute("SELECT column_name FROM system_schema.columns where keyspace_name = 'pitest' and table_name = '" + table + "'")
        for Row in columnRows:
            columns.append(Row.column_name)

        if set(lowerParList) == set(columns):     #Verificar se as chaves do json correspondem aos parametros da tabela a ser analisada 
            return True  
    return False                                  #Se nunca se verificar retorna falso

#Função para criar tabelas
def createTables(flatJson):

    strCommand = "create table table1(pk text"      #Começar a string de comando que cria a tabela principal

    for key in flatJson.keys():                     #Para cada chave do flatJson
        key = key.lower()
        strCommand = strCommand + ", " + key + " text"  #Adicionar à string do comando que cria a tabela principal   
        session.execute("create table table1_" + key + "(pk text," + key + " text, PRIMARY KEY(" + key + "))" )  #Criar a tabela secundária correspondente a essa chave

    strCommand = strCommand + ", PRIMARY KEY(pk)) "  #Acabar a string de comando após todos os parametros serem adicionados e correr o comando
    session.execute(strCommand)

#Função de inserção de um json
def insertInto(table, flatJson):
 
    if not checkTable(flatJson):               #Verificar se existem tabelas em que os dados possam ser inseridos
        createTables(flatJson)                 #Caso não exista chamar a função que cria
   
    strInsert = "insert into " + table + "(pK"  #strInsert é a string de instrução / O que escreveriamos se estivessemos a inserir por terminal 
   
    pkVal = ""                                 #pkVal é o valor do parametro primary key que identifica a tabela
  
    for key in flatJson.keys():                  #Percorrer as chaves do dicionário de forma a inserir os campos da tabela na string de instrução e formar o pkVal 
        pkVal = pkVal + flatJson[key]
        strInsert = strInsert + ", " + key 
   
    strInsert = strInsert + ") values('" + pkVal + "'"          #Acabar os campos da tabela e começar a inserir os valores na string
    
    for key in flatJson.keys():                                 #Ciclo para adicionar os valores à string de instrução
        strInsert = strInsert + ", '" + flatJson[key] + "'"
    
    strInsert = strInsert + ")"       #Fechar a string 
    
    print(strInsert)                  #Print e executar o comando
    session.execute(strInsert)
    
    insertSecondaryTables(table, flatJson, pkVal)               #Inserir os dados nas tabelas adicionais para se poder fazer querying complexo

#Função de inserção nas tabelas secundárias
def insertSecondaryTables(table, flatJson, pk):

    for key in flatJson.keys():          #Para cada parametro do flatJson adicionar a informação às tabelas adicionais 
        insertStr = "insert into " + table + "_" + key + " (pK, " + key + ") values('" + pk + "', '" +  flatJson[key] + "')"
        session.execute(insertStr)


insertInto("table1", json)
