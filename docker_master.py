import time 
from docker_api import *
import utils as ut

NODE_MAP = {
    "core": "10.12.0.15",
    "edge-tr-1":"10.2.0.20"
}

def check_cost_and_migrate():
    """
    "migrate" webserver based on dynamically
    changing cost
    """
    def get_min_cost_region():
        #get the cost map
        with open("cost.txt") as cost:
            cost = map(lambda line: line.strip().split(","), cost.readlines())
            cost_map = {c[0]:int(c[1]) for c in cost}
        
        min_region, min_cost = cost_map.popitem() 
        for region, cost in cost_map.items():
            if cost < min_cost:
                min_cost = cost
                min_region = region

        return min_region

    started = False
    while True: 
        #The service has not been started
        #should only happen once
        if not started:
            region = get_min_cost_region()
            print "starting WordPress on {}".format(region)
            deploy_webserver(region=region)
            print "WordPress running on {}:8080".format(NODE_MAP[region])
            started = True
        else:
            new_region = get_min_cost_region()
            if new_region != region:
                print "migrating WordPress from {} to {}".format(region, new_region)

                #first migrate the volume
                ut.copy_files("/home/ubuntu/", "mysql_volume", NODE_MAP[region], NODE_MAP[new_region])
               
                #stop/remove the current deployment
                remove_webserver()

                #start the new deployment
                deploy_webserver(region=new_region)
                print "WordPress running on {}:8080".format(NODE_MAP[new_region])
                region = new_region
        
        time.sleep(10)

if __name__ == "__main__":
    #for cont in get_containers(): print cont["Names"][0]

    #cont_id = create_container()
    #cont_id = create_container(image="training/webapp", cmd=["/usr/bin/python app.py"])
    
    #create_web_server(db=True)
    #time.sleep(60)
    #create_web_server(db=False)

    #print "created container with ID {}".format(cont_id)
    #print start_container(cont_id)
    check_cost_and_migrate()



