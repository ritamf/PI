import time
import random
import json 
import requests
import matplotlib.pyplot as plt
import ast
import statistics
from scipy.stats import norm

START_DATE = time.time()
TOKEN = 'KCGL0vj1j7sk5xWApRA0BITFlH_2ATneYWju3GHVgdI/'
ENDPOINT_INSERT = 'http://10.0.12.65:8000/insert_into_db/'
ENDPOINT_QUERY = 'http://10.0.12.65:8000/query_db/'
REPEAT_X_TIMES = 100
INSERT_NUM = 20
times = []

def sendInfo():

    data = ""
    average = 0
    
    for i in range(INSERT_NUM):
        if random.randrange(2) == 1:
            data = data1()
        else:
            data = data2()
        #url = ENDPOINT_INSERT+TOKEN+str(random.randrange(5))
        #gcontext = ssl.SSLContext()
        #response = urllib.requests.urlopen(url, data, context=gcontext).read()
        headersS = {"content_type":"application/json"}
        print(i)
        start = time.time()
        r = requests.post(url=ENDPOINT_INSERT+TOKEN+str(random.randrange(5)), json=ast.literal_eval(json.dumps(data)), headers=headersS)
        finish = time.time()
        average = average + (finish - start)
    average = average / INSERT_NUM
    return average

def testQueries():

    #rangedSensorQuery
    start_time1 = time.time()
    data = {"conditions":[["temperature", ">", "13"]] , "attributes":["temperature", "humidity"] , "from_ts": str(START_DATE), "to_ts":str('2021-08-01 22:36:20.785976')}
    requests.post(ENDPOINT_QUERY+TOKEN+str(random.randrange(5)), data, verify=False)
    finish_time1 = time.time()

    #sensorQuery
    start_time2 = time.time()
    data = {"conditions":[["temperature", ">", "13"]] , "attributes":["temperature", "humidity"] , "from_ts": "", "to_ts":""}
    requests.post(ENDPOINT_QUERY+TOKEN+str(random.randrange(5)), data, verify=False)
    finish_time2 = time.time()

    #rangedUserQuery
    start_time3 = time.time()
    data = {"conditions":[["temperature", ">", "13"]] , "attributes":["temperature", "humidity"] , "from_ts": str(START_DATE), "to_ts":str('2021-08-01 22:36:20.785976')}
    requests.post(ENDPOINT_QUERY+TOKEN+"all", data, verify=False)
    finish_time3 = time.time()

    #userQuery
    start_time4 = time.time()
    data = {"conditions":[["temperature", ">", "13"]] , "attributes":["temperature", "humidity"] , "from_ts": "", "to_ts":""}
    requests.post(ENDPOINT_QUERY+TOKEN+"all", data, verify=False)
    finish_time4 = time.time()

    return [finish_time1-start_time1, finish_time2-start_time2, finish_time3-start_time3, finish_time4-start_time4]

def setTimeValues(timesList):
    i = 0
    while i < len(timesList):
        times[i].append(timesList[i])
        i = i+1

def testProcess(numRepeats, times):
    i=0
    while i<numRepeats:
        times[0].append(sendInfo())
        #queryTimes = testQueries()
        #setTimeValues(queryTimes)
        i=i+1

def data1():
    data = {"temp": str(random.uniform(-10.0, 40.0)), "hum": str(random.uniform(0.0, 100.0)), "press": str(random.uniform(0.987, 1.0))}
    json_data = json.dumps(data)
    return [data]

def data2():
    data = {"temp": str(random.uniform(-10.0, 40.0)), "humi": str(random.uniform(0.0, 100.0)), "pres": str(random.uniform(0.987, 1.0))}
    json_data = json.dumps(data)
    return [data]

def graph(timesList):
    for sample in timesList:
        plt.plot([i+1 for i in range(REPEAT_X_TIMES)], sample)
        #plt.plot(sample, norm.pdf(sample, statistics.mean(sample), statistics.stdev(sample)),'ro')
        plt.xlabel("number of sequence iterations (1 iteration = inserting 100 jsons)")
        plt.ylabel("average time taken per insertion (seconds)")
        plt.errorbar([i+1 for i in range(REPEAT_X_TIMES)], sample, yerr=statistics.variance(sample), fmt='.k')
        plt.show()

insertTimes = []
rangedSensorQueryTimes = []
sensorQueryTimes = []
rangedUserQueryTimes = []
userQueryTimes = []

#times.append(rangedSensorQueryTimes)
#times.append(sensorQueryTimes)
#times.append(rangedUserQueryTimes)
#times.append(userQueryTimes)
times.append(insertTimes)

testProcess(REPEAT_X_TIMES, times)
graph(times)











