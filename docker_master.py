import requests
import json
import pdb
import time 
from consts import MASTER_URL
#API v1.19:
#https://docs.docker.com/v1.8/reference/api/docker_remote_api_v1.19/

#There is a docker python API
#https://github.com/docker/docker-py

def get_url(path):
    return MASTER_URL + path

def get_containers():
    #Get all the containers
    #curl -s -XGET $MASTER_URL/containers/json?all=1  
    r = requests.get(get_url("/containers/json?all=1"))
    print r.json()

def create_container(region="r1", name="span_test"):
    #Example containing all parameters
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
        "Image":"ubuntu", 
        "Cmd":["/bin/bash"],  
        #need the following 3 to be able to attach
        "AttachStdin": True, 
        "Tty":True,
        "OpenStdin":True,
        "ExposedPorts": {
                 "22/tcp": {}
        },
        #Scheduling filters are passed as env vars
        "Env": [ 
            "constraint:region=={}".format(region) 
        ],
    }

    headers = {"Content-Type": "application/json"}
    r = requests.post(get_url("/containers/create?name={}".format(name)), 
            data=json.dumps(data), headers=headers)

    print r.status_code

    if r.status_code == 201:
        cont_id = r.json()["Id"]

    return cont_id    

def start_container(cont_id):
    r = requests.post(get_url("/containers/{}/start".format(cont_id)))
    print r.status_code
    
def stop_container(cont_id):
    r = requests.post(get_url("/containers/{}/stop".format(cont_id)))
    print r.status_code
    
def remove_container(cont_id):
    r = requests.delete(get_url("/containers/{}".format(cont_id)))
    print r.status_code
    

def check_cost_and_migrate():
    def get_min_cost_region():
        #get the cost map
        with open("cost.txt") as cost:
            cost = map(lambda line: line.strip().split(","), cost.readlines())
            cost_map = {c[0]:int(c[1]) for c in cost}

        region = "r1" if cost_map["r1"] < cost_map["r2"] else "r2"
        return region

    started = False
    while True: 
        #The service has not been started
        #should only happen once
        if not started:
            region = get_min_cost_region()
            print "starting container on {}".format(region)
            cont_id = create_container(region=region)
            start_container(cont_id)
            started = True
        else:
            new_region = get_min_cost_region()
            if new_region != region:
                print "migrating from {} to {}".format(region, new_region)
                region = new_region

                stop_container(cont_id)
                remove_container(cont_id)

                cont_id = create_container(region=region)
                start_container(cont_id)

        time.sleep(10)
            
    


if __name__ == "__main__":
    #get_containers()
    #cont_id = create_container()
    #print "created container with ID {}".format(cont_id)
    #start_container(cont_id)
    check_cost_and_migrate()
