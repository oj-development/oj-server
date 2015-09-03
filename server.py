import socket,threading,subprocess,json,os,time,base64,random,shutil,uuid,hashlib
from result_name import *
compiler={"pas":"fpc","c":"gcc","cpp":"g++"}
def answer_compare(a,b,method):
    if method&1!=0:
        a=a.replace("\r","")
        b=b.replace("\r","")
    if method&8!=0:
        a=a.replace(" ","")
        b=b.replace(" ","")
    if method&16!=0:
        a=a.lower()
        b=b.lower()
    a=a.split("\n")
    b=b.split("\n")
    if method&2!=0:
        a=list(map(str.strip,a))
        b=list(map(str.strip,b))
    if method&4!=0:
        while a[-1]=="":
            a.pop()
        while b[-1]=="":
            b.pop()
    return a==b
def runcode(indata,outdata,timeout,setting,mlimit,tempdir):
    point_status=None
    pac_score=0
    if os.name=='posix':
        runname="ulimit -m "+str(mlimit)+";"+os.path.join(tempdir,'temp')
    else:
        runname=os.path.join(tempdir,'temp')
    test_process=subprocess.Popen([runname], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=tempdir)
    if setting["input"]!="":
        if setting["judgemode"]&1==0:
            with open(setting["input"], 'wb') as f:
                f.write(indata.encode("utf-8"))
        else:
            with open(setting["input"], 'w') as f:
                f.write(indata+"\n")
    start = time.time()
    try:
        if setting["input"]=="":
            if setting["judgemode"]&1==0:
                output,err=test_process.communicate(indata.encode("utf-8"),timeout)
            else:
                output,err=test_process.communicate((indata+"\n").encode("utf-8"),timeout)
        else:
            output,err=test_process.communicate(None,timeout)
    except subprocess.TimeoutExpired as e:
        point_status=jresult.TLE
        test_process.kill()
        output,err=test_process.communicate()
    except MemoryError as e:
        point_status=jresult.MLE
        test_process.kill()
        output,err=test_process.communicate()
    except BrokenPipeError as e:
        test_process.kill()
        output,err=test_process.communicate()
    end = time.time()
    if point_status==None:
        if test_process.returncode>0:
            point_status=jresult.RE
        else:
            if setting["output"]!='':
                with open(setting["output"], 'rb') as f:
                    output=f.read().decode("utf-8")
            elif output==None:
                output=""
            else:
                output=output.decode("utf-8")
            if "sj_program" in setting:
                if os.name=='posix':
                    sj_runname=os.path.join(tempdir,"sjtemp")
                    sj_filename=sj_runname
                else:
                    sj_runname=os.path.join(tempdir,"sjtemp")
                    sj_filename=sj_runname+".exe"
                if not os.path.isfile(sj_filename):
                    with open(sj_filename, 'wb') as f:
                        f.write(base64.b64decode(setting["sj_program"].encode("utf-8")))
                sj_input=setting["input"]
                sj_output=setting["output"]
                if (sj_input=="") and setting["sj_param"].find("%i")>-1:
                    sj_input=os.path.join(tempdir,"temp.in")
                    with open(sj_input, 'wb') as f:
                        f.write(indata.encode("utf-8"))
                if sj_output=="":
                    sj_output=os.path.join(tempdir,"temp.out")
                    with open(sj_output, 'wb') as f:
                        f.write(output.encode("utf-8"))
                sj_outdata=os.path.join(tempdir,"test.ans")
                with open(sj_outdata, 'wb') as f:
                    f.write(outdata.encode("utf-8"))
                sj_process=subprocess.Popen([sj_runname,setting["sj_param"].replace("%i",sj_input).replace("%o",sj_output).replace("%a",sj_outdata)], stdout=subprocess.PIPE)
                try:
                    sj_output,sj_err=sj_process.communicate(None,10)
                except subprocess.TimeoutExpired as e:
                    point_status=jresult.WA
                if point_status==None:
                    if sj_process.returncode>0:
                        point_status=jresult.WA
                    else:
                        if setting["sj_type"]==0:
                            point_status=jresult.AC
                        else:
                            sj_result=sj_output.split()
                            sj_result[0]=int(sj_result[0])
                            err+=sj_result[1]
                            if sj_result[0]==0:
                                point_status=jresult.WA
                            else:
                                point_status=jresult.PAC
                                pac_score=sj_result[0]
            else:
                if not answer_compare(output,outdata,setting["judgemode"]):
                    point_status=jresult.WA
                else:
                    point_status=jresult.AC
    if err==None:
        err=""
    else:
        err=err.decode("utf-8")
    return ([point_status.value,end-start,err],pac_score)
def tcplink(sock, addr):
#    sock.send(b'Welcome!')
    r=str(random.random())[2:]
    tempdir=os.path.join('temp',r)
    while os.path.isdir(tempdir):
        r=str(random.random())[2:]
        tempdir=os.path.join('temp',r)
    os.mkdir(tempdir)
    record=sock.recv(1024000000)
#    print(record)
    record_hash=str(uuid.uuid4())
    record=json.loads(record.decode('utf-8'))
    mode=record[0]
    if (mode==0) or (mode==1):
        record=record[1]
        cachefile=os.path.join("cache",record[2]+".json")
        if os.path.isfile(cachefile):
            with open(cachefile, 'r') as f:
                data=json.loads(f.read())
        else:
            sock.send(json.dumps([1,record[2]]).encode('utf-8'))
            data=sock.recv(1024000000)
            md5 = hashlib.md5()
            md5.update(data)
            try_count=0
            while md5.hexdigest()!=record[2]:
                try_count=try_count+1
                sock.send(json.dumps([4,try_count]).encode('utf-8'))
                newdata=sock.recv(1024000000)
                data=data+newdata
                md5.update(newdata)
            data=data.decode('utf-8')
            with open(cachefile, 'w') as f:
                f.write(data)
            data=json.loads(data)
        if mode==1:
            sock.send(json.dumps([2,record_hash]).encode('utf-8'))
            sock.close()
#        print(record)
        file_name=os.path.join(tempdir,'temp.'+record[1][0])
        setting=record[0]
        if setting["input"]!="":
            setting["input"]=os.path.join(tempdir,setting["input"])
        if setting["output"]!="":
            setting["output"]=os.path.join(tempdir,setting["output"])
        with open(file_name, 'w') as f:
            f.write(record[1][1])
        p=subprocess.Popen([compiler[record[1][0]],file_name], stdout=subprocess.PIPE)
        log=p.communicate()[0].decode('utf-8')
#        print(log)
        score=0
        if p.returncode>0:
            status=[[jresult.CE.value,0,""]]
        else:
            status=[]
#            i=0
            for x in data:
#                i=i+1
                point_result=runcode(x[0],x[1],x[3],setting,x[4],tempdir)
                status.append(point_result[0])
                if status[-1][0]==jresult.AC.value:
                    score+=x[2]
                elif status[-1][0]==jresult.PAC.value:
                    score+=point_result[1]
        judge_result=json.dumps([0,[status,score,log]])
        if mode==0:
            sock.send(judge_result.encode('utf-8'))
            sock.close()
        else:
            with open(os.path.join("temp",record_hash+".json"), 'w') as f:
                f.write(judge_result)
        time.sleep(1)
        shutil.rmtree(tempdir)
    elif mode==2:
        file_name=os.path.join("temp",record[1]+".json")
        if os.path.isfile(file_name):
            with open(file_name, 'r') as f:
                sock.send(f.read().encode('utf-8'))
        else:
            sock.send(json.dumps([3]).encode('utf-8'))
if os.path.isfile("temp"):
    os.remove('temp')
if not os.path.isdir("temp"):
    os.mkdir('temp')
if os.path.isfile("cache"):
    os.remove('cache')
if not os.path.isdir("cache"):
    os.mkdir('cache')
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('127.0.0.1', 28522))
s.listen(5)
#p = Pool()
while True:
    sock, addr = s.accept()
    t = threading.Thread(target=tcplink, args=(sock, addr))
    t.start()
