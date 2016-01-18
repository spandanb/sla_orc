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

def _create_container(name="", data=None):
    headers = {"Content-Type": "application/json"}
    if not name:
        api_endpoint = get_url("/containers/create")
    else:
        api_endpoint = get_url("/containers/create?name={}".format(name))
    r = requests.post(api_endpoint,
            data=json.dumps(data), headers=headers)
    return r
    
def create_web_server(db=True):
    #Doesn't work
    #See: https://hub.docker.com/_/wordpress/
    #https://hub.docker.com/_/mysql/
    #http://www.sitepoint.com/how-to-use-the-official-docker-wordpress-image/
    if db:
        #create DB
        data = {
            "Image": "span/mysql:v2", #"mysql:latest",
            "ExposedPorts": {
                     "3306/tcp": {}
            },
            "Env": [
                "MYSQL_ROOT_PASSWORD=password",
                "MYSQL_DATABASE=wordpress"
            ]
        } 
        r = _create_container(name="mydb2", data=data)
        print r.status_code
        print start_container(r.json()["Id"])
    else:
        #create web server
        data = {
            "Image": "wordpress:latest", 
            "ExposedPorts": {
                     "80/tcp": {}
            },
            "Env": [
                "WORDPRESS_DB_PASSWORD=password"
            ],
            "HostConfig":{
                "PortBindings": { "80/tcp": [{ "HostPort": "8080" }] },
                "Links":["mydb2:mysql"]
            }
        }
    
        print "Starting webserver"
        r = _create_container(name="mywp2", data=data)
        print r.status_code
        print start_container(r.json()["Id"])
    

def create_web_server2():
    """Uses the tutum/wordpress image with 
    wordpress + db in same image
    """
    data = {
        "Image":"tutum/wordpress",
        "ExposedPorts": {
                 "80/tcp": {}
        },
        "HostConfig":{
            "PortBindings": { "80/tcp": [{ "HostPort": "8080" }] },
        }
    }

    print "Starting webserver"
    r = _create_container(name="webserver", data=data)
    print r.status_code
    print start_container(r.json()["Id"])
    

def start_container(cont_id):
    return requests.post(get_url("/containers/{}/start".format(cont_id)))
    
def stop_container(cont_id):
    return requests.post(get_url("/containers/{}/stop".format(cont_id)))
    
def remove_container(cont_id):
    return requests.delete(get_url("/containers/{}".format(cont_id)))

def remove_recent(force=True):
    """
    Stop and remove containers created in 
    last 45 minutes
    """
    #epoch time
    current_time = int(time.time()) 

    for cont in get_containers():
        if current_time - cont["Created"] < 45 * 60:
            print "deleting {} [{}]".format(cont["Id"], cont["Names"][0])
            if force: stop_container(cont["Id"])
            remove_container(cont["Id"])

if __name__ == "__main__":
    remove_recent()



