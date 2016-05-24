Sets up docker engine on hosts

Then sets up swarm on all the nodes

NB: The master already runs the docker engine and is
part of the swarm. Don't need to specify the master as a 
slave as well- since this is already the default.

Docker Swarm Command
====================
Once docker swarm is setup

sudo docker -H :4000 ps

sudo docker -H tcp://0.0.0.0:4000 run -dit -P -e constraint:region==r1 --name test1 ubuntu


Usage:
ansible-playbook -i ./hosts --extra-vars master_ip=10.12.1.23 docker_setup.yaml -v -f 10


