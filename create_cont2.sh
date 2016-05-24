#!/bin/bash

#create container
curl -X POST -H "Content-Type: application/json" -d '{"Image":"ubuntu", "Cmd":["/bin/bash"]}' http://10.12.0.14:8000/containers/create?name=span_foo

#run container
#curl -v -X POST -H "Content-Type: application/json" -d '{"PortBindings": { "5000/tcp": [{ "HostPort": "5000" }] },"RestartPolicy": { "Name": "always",},}' http://localhost:2376/containers/registry/start?name=registry

