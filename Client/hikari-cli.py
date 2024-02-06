import os, json, time, subprocess, requests
import sys

def judgePts(execPath,inData,outData,timeLimit,memLimit):
    #测试
    obj = subprocess.Popen([execPath],shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        obj.stdin.write(inData.encode('utf-8'))
        output,err = obj.communicate(timeout = timeLimit)
    except subprocess.TimeoutExpired:
        obj.kill()
        return {'stat':'TLE','out':'(Time Limit Exceeded.)','ans':outData}
    
    if err:
        return {'stat':'RE','out':err,'ans':outData}
        
    #比对程序输出
    if (((output.decode('utf-8')).replace('\n','')).replace(' ','')).strip() == (((outData).replace('\n','')).replace(' ','')).strip(): #去除回车和空格
        return {'stat':'AC','out':output,'ans':outData}
    else:
        return {'stat':'WA','out':output,'ans':outData}

def judge(data,code,language ='cpp'):
    os.mkdir('Temp')
    resultDict = {'stat':'AC'}
    score = 0

    runID = str(time.time()) # 测试ID
    sourcePath ='Temp\\' + runID + '.' + language #源文件路径
    execPath =  'Temp\\' + runID + '.exe' #执行文件路径
    cplogPath = 'Temp\\' + runID + '.log' #编译信息路径
    # 写源文件
    with open(sourcePath,'w') as f:
        f.write(code)
    
    compileCommands = { #编译命令
        'cpp':f'Compilers\\Mingw64\\bin\\g++.exe {sourcePath} -o {execPath} > {cplogPath} 2>&1',
        'c':f'Compilers\\Mingw64\\bin\\gcc.exe {sourcePath} -o {execPath} > {cplogPath} 2>&1'
    }
    #执行编译
    os.system(compileCommands[language])

    compileLog = ''
    with open(cplogPath,'r') as f:
        compileLog = f.read()
    
    #找不到编译出的可执行文件，就报Compile Error
    if not os.path.exists(execPath):
        return {'stat':'CE','log':compileLog}
    else: resultDict['log'] = compileLog

    #逐点测试
    for i in data['data'].keys():
        resultDict[i] = judgePts(execPath,data['data'][i]['in'],data['data'][i]['out'],data['time_limit'],data['mem_limit'])
        score += data['data'][i]['score'] if resultDict[i]['stat'] == 'AC' else 0 #如果AC加上对应score
        if resultDict['stat'] == 'AC' and resultDict[i]['stat'] != 'AC':
            resultDict['stat'] = resultDict[i]['stat']

    #删除临时文件
    os.unlink(sourcePath)
    os.unlink(execPath)
    os.unlink(cplogPath)
    os.rmdir('Temp')
    resultDict['score'] = score
    return resultDict    

"""
Usage:

with open("./1001.json",'r') as f:
        print(judge(json.loads(f.read()),'''
              #include <bits/stdc++.h>
              using namespace std;
              
              int main(){
                int a,b;
                cin>>a>>b;
                cout<<a+b;
                return 0;
              }
              ''','cpp'))

Json Example:
{
    "pid":1001,
    "time_limit":1,
    "mem_limit":1000,
    "data_cnt":2,
    "data":{
        "1":{"in":"1 1","out":"2","score":50},
        "2":{"in":"2 3","out":"5","score":50}
    }
}
"""

def judgeWithURL(dataURL,code,language='cpp'):
    try:
        jsonData = requests.get(dataURL)
        return judge(jsonData.json(),code,language)
    except Exception as e:
        print (e)
        return {'stat':'UKE','log':str(e)}


#传参方式：python3 hikari-cli.py "http://124.220.133.192/1001.json" test.cpp
if __name__ == '__main__':
    try:
        code = ''
        with open(sys.argv[2],'r') as f:
            code = f.read()

        print(judgeWithURL(sys.argv[1],code,'cpp'))
    except Exception as e:
        print("Exception:",str(e))