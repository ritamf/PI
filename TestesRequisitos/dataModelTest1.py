from cassandra.cluster import Cluster

#Ligação ao cluster, neste caso um cluster de testes local que criei previamente
from pip._vendor.requests import ReadTimeout

cluster = Cluster()
session = cluster.connect('pitest')

global table_id
table_id = 1


json = {"sensorId" : "0002",
"timeStamp" : "2020-06-01 10:10:10",
"temperature" : "10"}
#É criada uma tabela de tabelas (metadata), uma tabela por cada grupo de atributos de json e tabelas secundárias dos valores de cada um
#pK é o parametro que identifica este registo em especifico e é passado pela API
#Neste caso teremos a table1 com pK = UUID1, sensorId = 0001, timeStamp = 2020-06-01 10:10:10 e temperature = 10
#table1_sensorId com table = table1_sensorId pK = UUID1 e sensorId = 0001
#table1_timeStamp com table = table1_timeStamp pK = UUID1  e timeStamp = 2020-06-01 10:10:10
#table1_temperature com table = table1_temperature pK = UUID1 e temperature = 10


session.execute("create table metadata (tableName text, tableAtributes list, PRIMARY KEY(tableAtributes) )")



#Função para verificar se já existe uma tabela na qual o json possa ser inserido
def checkTable(flatJson):
 
    lowerParList = []                          #Criar uma lista com todos os parametros do flat json em minisculas => Porque o cassandra vai ter as colunas em miniscula
    for par in flatJson.keys():
        lowerParList.append(par.lower())
 
    lowerParList.append('pk')                  #Adicionar pk porque estará em todas as tabelas


    #procurar na tabela metadata o tableName quando a lista dos atributos é igual aos parametros do flat json
    #retorna o nome se já houver ou retorna null se não existe ainda essa tabela 
    table = session.execute("SELECT * FROM metadata WHERE tableAtributes = " + str(lowerParList) )
    return table.tableName


#Função para criar tabelas
def createTables(flatJson):

    table_name = "table"+ table_id

    table_id += 1
  

    strCommand = "create table " + table_name + "(pk text"      #Começar a string de comando que cria a tabela principal
    lowerParList = []
    for key in flatJson.keys():                     #Para cada chave do flatJson
        lowerParList.append(key.lower())
        key = key.lower()
        strCommand = strCommand + ", " + key + " text"  #Adicionar à string do comando que cria a tabela principal   
        session.execute("create table "+ table_name + "_" + key + " (table text, pk text," + key + " text, PRIMARY KEY( table, " + key + "))" )  #Criar a tabela secundária correspondente a essa chave

    lowerParList.append('pk') 
    strCommand = strCommand + ", PRIMARY KEY(pk)) "  #Acabar a string de comando após todos os parametros serem adicionados e correr o comando
    session.execute(strCommand)


    session.execute("insert into metadata (tableName, tableAtributes) values (" + table_name + ", " + lowerParList +")")


    return table_name                               #retorna o table_name da tabela principal criada

#Função de inserção de um json
def insertInto(flatJson, pk_id):                    #os parametros são o jason e a pk que será passada pela API
    table_name = checkTable(flatJson)              #Verificar se existem tabelas em que os dados possam ser inseridos
    if not table_name:
        table_name = createTables(flatJson)                       #Caso não exista chamar a função que cria que retorna o seu nome (da principal)
   
    strInsert = "insert into " + table_name + "(pK"  #strInsert é a string de instrução / O que escreveriamos se estivessemos a inserir por terminal 
   
  
    for key in flatJson.keys():                   
        strInsert = strInsert + ", " + key 
   
    strInsert = strInsert + ") values('" + pk_id + "'"          #Acabar os campos da tabela e começar a inserir os valores na string
    
    for key in flatJson.keys():                                 #Ciclo para adicionar os valores à string de instrução
        strInsert = strInsert + ", '" + flatJson[key] + "'"
    
    strInsert = strInsert + ")"       #Fechar a string 
    
    print(strInsert)                  #Print e executar o comando
    session.execute(strInsert)
    
    insertSecondaryTables(table_name, flatJson, pk_id)               #Inserir os dados nas tabelas adicionais para se poder fazer querying complexo

#Função de inserção nas tabelas secundárias
def insertSecondaryTables(table, flatJson, pk):

    for key in flatJson.keys():          #Para cada parametro do flatJson adicionar a informação às tabelas adicionais 
        insertStr = "insert into " + table + "_" + key + " (table, pK, " + key + ") values('" + table + "','" + pk + "', '" +  flatJson[key] + "')"
        session.execute(insertStr)


insertInto(json,1)
