#!/bin/bash
#script to setup docker screen session
#Usage: screen_helper_master.sh <<key value store IP>> <<region name>> 

create_session(){
    #create screen session
    #Arguments:
    #$1: screen session name
    screen -S $1 -d -m
}

screen_it(){
    #creates new tabs and runs command
    #Arguments:
    #$1: screen session name
    #$2: tab name 
    #$3: command to execute
    
    SESSION_NAME=$1
    TAB_NAME=$2
    CMD=$3

    screen -S $SESSION_NAME -X screen -t $TAB_NAME /bin/bash
    screen -S $SESSION_NAME -p $TAB_NAME -X stuff "$CMD$(printf \\r)"
}

send_kill(){
    #sends kill signal (Ctrl^c) to specific tab
    #Arguments:
    #$1: screen session name
    #$2: tab name or number, arg to -p
    
    screen -x $1 -p $2 -X stuff "^C"
}

#Check parameters
if [ "$#" -ne 1 ]; then
    echo "Usage: master_screen.sh <region>"
    exit 1
fi

#Parameter
MYIP="$(ifconfig | grep -A 1 'eth0' | tail -1 | cut -d ':' -f 2 | cut -d ' ' -f 1)"
KVSIP=$MYIP
REGION=$1
SESSION=docker

#create session
create_session $SESSION
#start consul
screen_it $SESSION cons "./consul agent -bootstrap -server -data-dir consul-data/ -bind $MYIP -client=0.0.0.0"
#stop docker
sudo service docker stop

#start docker daemon
#screen_it $SESSION dock "sudo docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --cluster-store=consul://$KVSIP:8500 --label region=$REGION --cluster-advertise=$MYIP:2376"
screen_it $SESSION dock "sudo docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock --label region=$REGION"

sleep 30

#start manager container
#screen_it $SESSION bash "sudo docker run -d -p 8000:2375 swarm manage -H tcp://0.0.0.0:2375 consul://$KVSIP:8500" 
screen_it $SESSION bash "sudo docker run -d -p 4000:4000 swarm manage -H :4000 --advertise $MYIP:4000 consul://$KVSIP:8500" 

sleep 30

#start container to join cluster
screen_it $SESSION bash "sudo docker run -d swarm join --advertise=$MYIP:2375 consul://$KVSIP:8500"

