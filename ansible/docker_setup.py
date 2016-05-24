import ansible_wrapper as ans

#There are two values of interest
#Only 1 node should be master, i.e. master==True
#
cluster = [
    {"ip": "10.12.0.15","master":True, "slave":True, "kv_store":True },
    {"ip": "10.12.0.14", "slave":True },
]

def get_hosts():
    #returns list of all hosts' IP addrs
    return [node['ip'] for node in cluster]

def get_master_ip():
    return next(node['ip'] for node in cluster if node['master'])
        
def get_inventory():
    """
    Returns an inventory of the following 
    format: 
    [master]
    X.X.X.X
    
    [slaves]
    X.X.X.X
    .
    .
    .
    """
    
    inv = """
[master]
{}

[slaves]""".format(get_master_ip())
    
    for node in cluster:
        inv += "\n{}".format(node["ip"])

    inv+="\n"

    return inv


def get_cluster_join_play(region, ip_addr, cluster_id):
    return """
---
- hosts: all
  remote_user: ubuntu
  tasks:
    - name: install daemon
      apt: name=daemon 
      become: true

    - name: run docker daemon 
      shell: daemon --name dockerd -- docker daemon -H --label region={} tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock 
      become: true

    - name: register node to swarm agent
      command: docker run -d swarm join --addr={}:2375 token://{}
    """.format(region, ip_addr, cluster_id)

def setup_swarm():
    #This playbook installs docker on all the hosts
    #and creates the cluster id
    hostsfile = ans.create_inventory(get_inventory())
    results = ans.playbook("docker_setup_play.yaml", hostsfile)
    ans.print_results(results)
    ans.remove_file(hostsfile)
    
    #The following sets up swarm 
    #get the cluster id from the master 
    with open('./from_host/{}/cluster_id.txt'.format(get_master_ip())) as cluster_id_file:
        cluster_id = cluster_id_file.readlines()[0].strip()
    
    #Now make each individual node join the cluster
    for node in cluster:
        region = node['region']
        play = get_cluster_join_play(region, node['ip'], cluster_id)
        ans.create_and_play(play, [node['ip']])


def main():

    

    for host in hosts:
        setup_docker(host)

if __name__ == "__main__":
    setup_swarm()
