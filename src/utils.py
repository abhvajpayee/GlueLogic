import os
import sys
import json
from os import path
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt
import json

def logtb(tmpdir, myhdltb, verilogtb, duration):
    f = open('myhdl.log', mode='w+t')
    sys.stdout = f
    myhdltb.config_sim(trace= True)
    myhdltb.run_sim(duration=duration)
    myhdltb.quit_sim()
    sys.stdout = sys.__stdout__
    f.flush()
    f.seek(0) 
    myhdltblines = f.readlines()
    f.close()
    f = open('verilog.log', mode='w+t')
    sys.stdout = f
    verilogtb.run_sim(duration=duration)
    sys.stdout = sys.__stdout__
    f.flush()
    f.seek(0) 
    verilogtblines = f.readlines()
    
    f.close() 

def functionStat(functName, fileName):
    statFile = 'stat.txt'
    if path.exists(statFile):
        with open(statFile) as json_file:
            data = json.load(json_file)
            if functName in data.keys():
                data[functName]['count'] = data[functName]['count'] + 1
                data[functName]['file']  = fileName
            else:
                data[functName] = {'count':1, 'file': fileName}
    else:
        data = {functName: {'count':1, 'file': fileName}}
    with open(statFile, 'w') as outfile:
        json.dump(data, outfile)
    
    '''functions = (list(data.keys()))
    stats = [data[key]['count'] for key in data.keys()]
    y_pos = np.arange(len(functions))
    fig = plt.figure(1)
    ax = fig.add_subplot(111)
    plt.bar(y_pos, stats, align='center', alpha=0.5)
    plt.xticks(y_pos, functions)
    plt.ylabel('Stats')
    plt.title('Function stats')
    ax.set_xticklabels(functions, rotation = 45, ha="right")
    plt.savefig('stats.png')'''

