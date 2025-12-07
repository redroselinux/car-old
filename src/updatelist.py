import os

import mirrors

def main():
    os.chdir("/tmp")
    allpkgs = []

    for i in mirrors.packagelist_places:
        print("Fetching "+i)
        os.system("curl -s -L -o list "+i)

        with open("list", "r") as f:
            list = f.read().splitlines()

        allpkgs.extend(list)

    with open("/etc/car/packagelist", "w") as f:
        f.write("")
        
    for i in allpkgs:
        with open("/etc/car/packagelist", "a") as f:
            f.write(i+"\n")
