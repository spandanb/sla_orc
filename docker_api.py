import requests
import sys
import json
import time
from consts import MASTER_URL

#API v1.19:
#https://docs.docker.com/v1.8/reference/api/docker_remote_api_v1.19/

#There is a docker python API
#https://github.com/docker/docker-py

def get_url(path):
    "return API endpoint"
    return MASTER_URL + path

def get_containers():
    #Get all the containers
    #curl -s -XGET $MASTER_URL/containers/json?all=1  
    r = requests.get(get_url("/containers/json?all=1"))
    return r.json()

def region_filter(region):
    """Scheduling filter
    based on region; can define other
    filters based on this pattern"""
    return ["constraint:region=={}".format(region) ]

def create_container(region="r1", 
                    name="span_test", 
                    image="ubuntu",
                    cmd=["/bin/bash"],
                    env=[]
    ):
    #list of all parameters
    data = {
         "Hostname": "",
         "Domainname": "",
         "User": "",
         "AttachStdin": False,
         "AttachStdout": True,
         "AttachStderr": True,
         "Tty": False,
         "OpenStdin": False,
         "StdinOnce": False,
         "Env": [
                 "FOO=bar",
                 "BAZ=quux"
         ],
         "Cmd": [
                 "date"
         ],
         "Entrypoint": "",
         "Image": "ubuntu",
         "Labels": {
                 "com.example.vendor": "Acme",
                 "com.example.license": "GPL",
                 "com.example.version": "1.0"
         },
         "Volumes": {
                 "/tmp": {}
         },
         "WorkingDir": "",
         "NetworkDisabled": False,
         "MacAddress": "12:34:56:78:9a:bc",
         "ExposedPorts": {
                 "22/tcp": {}
         },
         "HostConfig": {
           "Binds": ["/tmp:/tmp"],
           "Links": ["redis3:redis"],
           "LxcConf": {"lxc.utsname":"docker"},
           "Memory": 0,
           "MemorySwap": 0,
           "CpuShares": 512,
           "CpuPeriod": 100000,
           "CpuQuota": 50000,
           "CpusetCpus": "0,1",
           "CpusetMems": "0,1",
           "BlkioWeight": 300,
           "OomKillDisable": False,
           "PortBindings": { "22/tcp": [{ "HostPort": "11022" }] },
           "PublishAllPorts": False,
           "Privileged": False,
           "ReadonlyRootfs": False,
           "Dns": ["8.8.8.8"],
           "DnsSearch": [""],
           "ExtraHosts": None,
           "VolumesFrom": ["parent", "other:ro"],
           "CapAdd": ["NET_ADMIN"],
           "CapDrop": ["MKNOD"],
           "RestartPolicy": { "Name": "", "MaximumRetryCount": 0 },
           "NetworkMode": "bridge",
           "Devices": [],
           "Ulimits": [{}],
           "LogConfig": { "Type": "json-file", "Config": {} },
           "SecurityOpt": [""],
           "CgroupParent": ""
        }
    }

    data = {
        "Image": image, 
        "Cmd": cmd,  
        #need the following 3 to be able to attach
        "AttachStdin": True, 
        "Tty":True,
        "OpenStdin":True,
        "ExposedPorts": {
                 "22/tcp": {}, #Don't need this
                 "80/tcp": {}
        },
        #Scheduling filters are passed as env vars
        "Env": env, 
        "HostConfig":{
            "PortBindings": { "80/tcp": [{ "HostPort": "8080" }] },
        }
    }

    headers = {"Content-Type": "application/json"}
    r = requests.post(get_url("/containers/create?name={}".format(name)), 
            data=json.dumps(data), headers=headers)

    print r.status_code

    if r.status_code == 201:
        cont_id = r.json()["Id"]
    else:
        print "Received {}: {}".format(r.status_code, r.reason)
        sys.exit(1)

    return cont_id 

def create_container2():
    data = {
        "Image": "training/webapp", 
        "Cmd": ["python app.py"],
        "AttachStdout": False,
        "AttachStderr": False,
    }

    headers = {"Content-Type": "application/json"}
    r = requests.post(get_url("/containers/create"), 
            data=json.dumps(data), headers=headers)

    print r.status_code

    if r.status_code == 201:
        cont_id = r.json()["Id"]
    else:
        print "Received {}: {}".format(r.status_code, r.reason)
        sys.exit(1)

    return cont_id 
    
    

def start_container(cont_id):
    return requests.post(get_url("/containers/{}/start".format(cont_id)))
    
def stop_container(cont_id):
    return requests.post(get_url("/containers/{}/stop".format(cont_id)))
    
def remove_container(cont_id):
    return requests.delete(get_url("/containers/{}".format(cont_id)))

def remove_recent(force=True):
    """
    Stop and remove containers created in 
    last 30 minutes
    """
    #epoch time
    current_time = int(time.time()) 

    for cont in get_containers():
        if current_time - cont["Created"] < 30 * 60:
            print "deleting {} [{}]".format(cont["Id"], cont["Names"][0])
            if force: stop_container(cont["Id"])
            remove_container(cont["Id"])

if __name__ == "__main__":
    remove_recent()



