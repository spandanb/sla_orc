#!/bin/bash

curl -X POST -H "Content-Type: application/json" -d '{
       "Hostname": "",
       "Domainname": "",
       "User": "",
       "AttachStdin": false,
       "AttachStdout": true,
       "AttachStderr": true,
       "Tty": false,
       "OpenStdin": false,
       "StdinOnce": false,
       "Env": [
               "FOO=bar",
               "BAZ=quux"
       ],
       "Cmd": [
               "date"
       ],
       "Entrypoint": "/bin/true",
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
       "NetworkDisabled": false,
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
         "OomKillDisable": false,
         "PortBindings": { "22/tcp": [{ "HostPort": "11022" }] },
         "PublishAllPorts": false,
         "Privileged": false,
         "ReadonlyRootfs": false,
         "Dns": ["8.8.8.8"],
         "DnsSearch": [""],
         "ExtraHosts": null,
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
}' http://10.12.0.14:8000/containers/create
