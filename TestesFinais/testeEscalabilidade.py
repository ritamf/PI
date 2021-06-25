import logging
import threading
import time
import requests
import random
import ast
import json
import matplotlib.pyplot as plt
import statistics

ENDPOINT_INSERT = 'http://10.0.12.65:8000/insert_into_db/'
tokens = ['753KgeyU-D0Ak0gSudUCzbgprS9Q5soRONBPnnUzApI/', 'i4pkxgEO8fihSuNL6rJM9dlUC95Ev60aACqZANZ8IAc/', 'NSsMrAlDhrpUiNxt-9qNiaF5IqxTpyuVccoZ_CeRKXY/', 'mysayD1pqap-CuHKLxkXalWE9VtQB6JqhK-PJ-2jlGc/', 'eEfnZJpolhIPLmtxRzqNSJNIDhddP9A8iwYQF35U4hA/', 'Lb97KpCxTRhfJz2jX00OeMTEu6ALwPbMQqQfYrE4Ig4/', '9WBm_Y63PfmZ4UlwW3NNRsbjjMKNN5yhdKovMecyDTE/', '6Qxb4bv_8f-76wny-J3dqWMVAWHT4qyoKYBzH1DLBtE/', 'fpa1k8s98jsznbMllz7j51GtTeQVkCNTwnY5t3tUyRI/', 'JyPiUBVTedfp-ZqHFxW04v5YTJS9BtY6TuwKk1hkKt0/','PVqgAv0GZGRXulhE-acnlztLW-QkV0fF0-ia7Ng9sXo/', '5q04Kgno2x7LoBU6xm6-pcK62VkILqH354NKScxANkA/']
NUM_THREADS = 8
REPEAT_X_TIMES = 80

def thread_function(name, token, sensorId, timesList):
    logging.info("Thread %s: starting", name)
    for i in range(REPEAT_X_TIMES):
        start = time.time()
        data = [{"temperature": str(random.uniform(-10.0, 40.0)), "humidity:": str(random.uniform(0.0, 100.0)), "pressure": str(random.uniform(0.987, 1.0))}]
        #jsonFile = json.dumps(data)
        headersS = {"content_type":"application/json"}
        requests.post(url=ENDPOINT_INSERT+token+str(sensorId), json=ast.literal_eval(json.dumps(data)), headers=headersS)
        finish = time.time()
        timesList[name].append(finish-start)
    logging.info("Thread %s: finishing", name)

def graph(sample):
    plt.plot([i+1 for i in range(10)], sample)
    plt.xlabel("number of active threads")
    plt.ylabel("average time per insert")
    plt.errorbar([i+1 for i in range(10)], sample, yerr=statistics.variance(sample), fmt='.k')
    plt.show()

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO,
                        datefmt="%H:%M:%S")

    threads = []
    threads_values = []
    
    for num in range(10):
        print(threads_values)
        times = []
        for i in range(num+1):
            times.append([])

        for index in range(num+1):
            logging.info("Main    : create and start thread %d.", index)
            x = threading.Thread(target=thread_function, args=(index,tokens[index],index,times))
            threads.append(x)
            x.start()

        for index, thread in enumerate(threads):
            logging.info("Main    : before joining thread %d.", index)
            thread.join()
            logging.info("Main    : thread %d done", index)

        averages = []
        for time_values in times:
            averages.append(sum(time_values) / len(time_values))
        threads_values.append(sum(averages) / len(averages))
        averages = []
        threads = []

    graph(threads_values)