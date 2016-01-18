import time 
from docker_api import *

def check_cost_and_migrate():
    """
    "migrate" VMs based on dynamically
    changing cost
    """
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
            cont_id = create_container(env=region_filter(region))
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
    #cont_id = create_container(image="training/webapp", cmd=["/usr/bin/python app.py"])
    
    create_web_server(db=True)
    time.sleep(60)
    create_web_server(db=False)

    #print "created container with ID {}".format(cont_id)
    #print start_container(cont_id)
    #check_cost_and_migrate()


