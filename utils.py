import os

def copy_files(dir_loc, dir_name, src_host, dest_host, username="ubuntu"):
    """
    Copy directory from src_host to dest_host
    """
    dir_path = dir_loc + dir_name
    #First src -> local
    os.system("scp -r {}@{}:{} . >/dev/null 2>&1".format(username, src_host, dir_path))
    #Then local -> dest
    os.system("scp -r ./{} {}@{}:{} >/dev/null 2>&1".format(dir_name, username, dest_host, dir_path))
    #rm local
    os.system("rm -rf ./{} >/dev/null 2>&1".format(dir_name))

def remove_volumes(dir_path="/home/ubuntu/mysql_volume", hosts=[]):
    for host in hosts:
        os.system("ssh ubuntu@{} 'sudo rm -rf {} > /dev/null 2>&1'".format(host, dir_path))

if __name__ == "__main__":
    CORE = "10.12.0.15"
    TR = "10.2.0.20"
    copy_files("/home/ubuntu/", "mysql_volume", CORE, TR)
