from cassandra.cluster import Cluster

class DB:

    #Inicializador
    def __init__(self, name):
        self.cluster = Cluster()
        self.session = self.cluster.connect(name)
        try:
            self.session.execute("create table metadata (tableName text, tableAtributes list<text>, PRIMARY KEY(tableName) )")
            self.session.execute("create table sensors (sensor_id text,user text ,tables list<text>, pks list<text>, PRIMARY KEY(user, sensor_id) )")
        except:
            pass

    # Função para verificar se já existe uma tabela na qual o json possa ser inserido
    def checkTable(self, flatJson):
        tableName = None
        lowerParList = []  # Criar uma lista com todos os parametros do flat json em minisculas => Porque o cassandra vai ter as colunas em miniscula
        for par in flatJson.keys():
            lowerParList.append(par.lower())

        lowerParList.append('pk')  # Adicionar pk porque estará em todas as tabelas


        tableAts = self.session.execute("SELECT * FROM metadata")  # Verifiar os dados da tabela de metadados

        for row in tableAts:
            if set(row[1]) == set(lowerParList):  # Se existir alguma tabela que já possua a mesma formatação retornar o seu nome
                tableName = row[0]
        return tableName  # Caso contrário retorna None

    # Função para criar tabelas
    def createTables(self, flatJson, pk_id):
        table_name = "table" + str(pk_id)  # Gerar nome da tabela principal // Não sei se este será a forma como vamos gerar nomes // Solução provisória

        strCommand = "create table " + table_name + "(pk text"  # Começar a string de comando que cria a tabela principal
        lowerParList = []  # Lista de parametros / Para colocar na tabela de metadados

        for key in flatJson.keys():  # Para cada chave do flatJson
            key = key.lower()
            lowerParList.append(key)  # Recolher os parametros para a tabela de metadados
            strCommand = strCommand + ", " + key + " text"  # Adicionar à string do comando que cria a tabela principal
            self.session.execute(
                "create table " + table_name + "_" + key + " (tableName text, pk text," + key + " text, PRIMARY KEY( tableName, " + key + ", pk))")  # Criar a tabela secundária correspondente a essa chave

        lowerParList.append('pk')
        strCommand = strCommand + ", PRIMARY KEY(pk)) "  # Acabar a string de comando após todos os parametros serem adicionados e correr o comando
        self.session.execute(strCommand)

        self.session.execute("insert into metadata(tableName, tableAtributes) values ('" + table_name + "', " + str(lowerParList) + ")")  # Adicionar a a tabela principal à tabela de metadados
        return table_name  # retorna o table_name da tabela principal criada
        
    # Função de inserção de um json
    def insertInto(self, flatJson, pk_id, sensor_id):  # os parametros são o json e a pk que será passada pela API

        pk_id = str(pk_id)
        table_name = self.checkTable(flatJson)  # Verificar se existe uma tabela em que os dados possam ser inseridos
        
        if not table_name:
            table_name = self.createTables(flatJson,pk_id)  # Caso não exista chamar a função que cria que retorna o seu nome (da principal)

        new_table_name = table_name

        strInsert = "insert into " + table_name + "(pK"  # strInsert é a string de instrução / O que escreveriamos se estivessemos a inserir por terminal

        for key in flatJson.keys():
            strInsert = strInsert + ", " + key

        strInsert = strInsert + ") values('" + pk_id + "'"  # Acabar os campos da tabela e começar a inserir os valores na string

        for key in flatJson.keys():  # Ciclo para adicionar os valores à string de instrução
            strInsert = strInsert + ", '" + flatJson[key] + "'"

        strInsert = strInsert + ")"  # Fechar a string

        print(strInsert)  # Print e executar o comando
        self.session.execute(strInsert)

        self.insertSecondaryTables(table_name, flatJson,
                            pk_id)  # Inserir os dados nas tabelas adicionais para se poder fazer querying complexo
        return new_table_name


    # Função de inserção nas tabelas secundárias
    def insertSecondaryTables(self, table, flatJson, pk):
        for key in flatJson.keys():  # Para cada parametro do flatJson adicionar a informação às tabelas adicionais
            insertStr = "insert into " + table + "_" + key + " (tableName, pK, " + key + ") values('" + table + "','" + pk + "', '" + \
                        flatJson[key] + "')"
            self.session.execute(insertStr)


    def insertIntoSensor(self, flatJson, pk_id, sensor_id, user):

        sensor_id = str(sensor_id)
        new_table_name = self.insertInto(flatJson, pk_id, sensor_id)                                                             #Inserir o registo com a função principal de inserção
        sensor = self.session.execute("SELECT * FROM sensors where user = '" + user +"' and sensor_id = '" + sensor_id + "'")    #Procurar pelo sensor na tabela de sensores
        tables = []
        pks = []

        if not sensor:                                               #Caso o sensor ainda não exista na tabela sensors adicionar
            if new_table_name is not None:                           
                tables.append(new_table_name)
                pks.append(str(pk_id))
                self.session.execute("insert into sensors (sensor_id, user, tables, pks) values ('" + sensor_id + "', '" + user + "', " + str(tables) + ", " + str(pks) + ") ")  # Adicionar a a tabela principal à tabela de metadados
        else:
            row = sensor.one()                                       #Se o sensor já existe mas esta formatação não é uma das associadas, adicionar ao parametro tables 
            tables = row[3]
            if new_table_name is not None and not new_table_name in tables:
                tables.append(new_table_name)
                self.session.execute("update sensors set tables = " + str(tables) + " where user = '" + user + "' and sensor_id = '" + sensor_id + "'")

        #Para qualquer registo adicionar o pk à lista de pks associados ao sensor
        sensor = self.session.execute("SELECT * FROM sensors where user = '" + user +"' and sensor_id = '" + sensor_id + "'")
        row = sensor.one()
        pks = row[2]
        if not str(pk_id) in pks:
            pks.append(str(pk_id))
            self.session.execute("update sensors set pks = " + str(pks) + " where user = '" + user + "' and sensor_id = '" + sensor_id + "'")


    def subQuery(self, table, param, condition):
        retList = []  # Lista de pks a retornar
        condition = condition[0] + "'" + condition[1:len(
            condition)] + "'"  # Alterar a formatação da condição para ser compativel com cql

        try:
            pkRows = self.session.execute("Select pk from " + table + "_" + param + " where tableName= '" + table + "' and " + param + condition)  # Executar a query secundária
            # print("Select pk from " + table + "_" + param + " where tableName= '" + table + "' and " + param + condition)

            for row in pkRows:  # Para cada pk retornado adicionar a lista de retorno
                retList.append(row[0])
        except:
            pass

        return retList


    # Função de querying geral
    def query(self, table, projList, paramConditionDictionary):
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
                self.subQuery(table, key, value))  # Adicionar a lista de resultados dessas subqueries à lista de listas das pks

        # print(pkLists)

        pks = set(pkLists[0]).intersection(*pkLists)  # Fazer a interceção de todas as listas para verificar que parametros correspondem a todas as filtragens
        # print(pks)

        rs = ""

        for pk in pks:  # Pesquisar na tabela principal e apresentar os resultados
            finalCommand = strCommand + "pk='" + pk + "'"
            # print(finalCommand)
            rows = self.session.execute(finalCommand)
            for row in rows:
                rs = rs + (str(row)[4:len(str(row)) - 1])
                rs = rs + ("\n")
                rs = rs + ("..........................................\n")
        
        return rs 

    def queryPerUser(self, user, projList, paramConditionDictionary):
        pkDict = {}  # Lista de listas de pks validadados pelas subqueries

        tableQuery = self.session.execute("select tables, pks from sensors where user = '" + user + "'") #Procurar para um utilizador as tabelas e pks associados
        tableLists = []
        userPkLists = []

        for row in tableQuery:                                              
            tableLists.append(row[0])
            userPkLists.append(row[1])

        tables = []
        userPks = []
        for tableList in tableLists:
            for table in tableList:
                tables.append(table)

        for userPkList in userPkLists:
            for userPk in userPkList:
                userPks.append(userPk)

        tables = list(dict.fromkeys(tables))             #Criar um set com valores unicos para as tabelas do utilizador e outro para os pks
        userPks = list(dict.fromkeys(userPks))

        for table in tables:        #Para cada tabela do utilizador efetuar as subqueries para obter os pks possiveis
            pkLists = []
            for key in paramConditionDictionary:  # Para cada conjunto de parametro e condição pelos quais queremos filtrar fazer uma subquery nas tabelas secundárias
                value = paramConditionDictionary[key]
                pkLists.append(self.subQuery(table, key, value))  # Adicionar a lista de resultados dessas subqueries à lista de listas das pks
            pkLists = set(pkLists[0]).intersection(*pkLists) #Criar um set de pks que passaram todos os requisitos associados a dada tabela
            pkDict[table] = pkLists

        rs = ""

        for key in pkDict:                  #Para cada tabela do utilizador
            for pk in pkDict[key]:          #Para cada pk possivel encontrado nas subqueries
                if pk in userPks:           #Se este é um dos pks do utilizador executar a query nessa tabela por esse pk
                    strCommand = "select "  # Adicionar ao comando os parametros que desejamos procurar
                    for par in projList:
                        strCommand = strCommand + par
                        if not projList[len(projList) - 1] == par:
                            strCommand = strCommand + ','
                    strCommand = strCommand + " from " + key + " where pk='" + pk + "'"  # Adicionar ao comando a tabela principal em que desejamos procurar
                    rows = self.session.execute(strCommand)
                    for row in rows:
                        rs = rs + (str(row)[4:len(str(row)) - 1])
                        rs = rs + "\n"
                        rs = rs + ("..........................................\n")
        return rs 

    def queryPerSensor(self, user, sensor, projList, paramConditionDictionary):
        pkDict = {}  # Lista de listas de pks validadados pelas subqueries

        tableQuery = self.session.execute("select tables, pks from sensors where user = '" + user + "' and sensor_id = '" + sensor + "'") #Procurar para um utilizador as tabelas e pks associados
        tableLists = []
        userPkLists = []

        for row in tableQuery:                                              
            tableLists.append(row[0])
            userPkLists.append(row[1])

        tables = []
        userPks = []
        for tableList in tableLists:
            for table in tableList:
                tables.append(table)

        for userPkList in userPkLists:
            for userPk in userPkList:
                userPks.append(userPk)

        tables = list(dict.fromkeys(tables))             #Criar uma lista com de valores unicos para as tabelas do utilizador e outro para os pks
        userPks = list(dict.fromkeys(userPks))

        for table in tables:        #Para cada tabela do utilizador efetuar as subqueries para obter os pks possiveis
            pkLists = []
            for key in paramConditionDictionary:  # Para cada conjunto de parametro e condição pelos quais queremos filtrar fazer uma subquery nas tabelas secundárias
                value = paramConditionDictionary[key]
                pkLists.append(self.subQuery(table, key, value))  # Adicionar a lista de resultados dessas subqueries à lista de listas das pks
            pkLists = set(pkLists[0]).intersection(*pkLists) #Criar um set de pks que passaram todos os requisitos associados a dada tabela
            pkDict[table] = pkLists

        rs = ""

        for key in pkDict:                      #Para cada tabela do utilizador
            for pk in pkDict[key]:              #Para cada pk possivel encontrado nas subqueries
                if pk in userPks:               #Se este é um dos pks do utilizador executar a query nessa tabela por esse pk
                    strCommand = "select "      #Adicionar ao comando os parametros que desejamos procurar
                    for par in projList:
                        strCommand = strCommand + par
                        if not projList[len(projList) - 1] == par:
                            strCommand = strCommand + ','
                    strCommand = strCommand + " from " + key + " where pk='" + pk + "'"  # Adicionar ao comando a tabela principal em que desejamos procurar
                    rows = self.session.execute(strCommand)
                    for row in rows:
                        rs = rs + (str(row)[4:len(str(row)) - 1])
                        rs = rs + "\n"
                        rs = rs + ("..........................................\n")
        return rs 

    #Função para apresentar as tabelas de registos existentes e que atributos possui cada tabela
    def showTables(self):
        tableRows = self.session.execute("Select * from metadata")
        for row in tableRows:
            print(row[0] + " - " + str(row[1]))

    #Função para mostrar os utilizadores existentes na base de dados
    def showUsers(self):
        userRows = self.session.execute("Select * from sensors")
        users = []
        for row in userRows:
            users.append(row[0])
        
        users = list(dict.fromkeys(users))

        for user in users:
            print(user)

    #Função que mostra as tabelas e atributos respetivos às mesmas mas apenas aquelas nas quais o utilizador tem registos
    def showMyTables(self, user):
        userRows = self.session.execute("Select * from sensors where user = '" + user + "'" )
        tables = []

        for row in userRows:
            for table in row[3]:
                tables.append(table)
        
        tables = list(dict.fromkeys(tables))

        for table in tables:
            result = self.session.execute("Select * from metadata where tableName = '" + table + "'")
            tableInfo = result.one()
            print(tableInfo[0] + " - " + str(tableInfo[1]))
