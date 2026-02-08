import os

import mirrors

def main():
    os.chdir("/tmp")
    allpkgs = []

    for repo, url in mirrors.packagelist_places:
        print("Fetching "+url)
        os.system("curl -s -L -o list "+url)

        with open("list", "r") as f:
            list = [line.strip() for line in f.read().splitlines() if line.strip()]

        allpkgs.extend([f"{repo}/{pkg}" for pkg in list])

    with open("/etc/car/packagelist", "w") as f:
        f.write("")
        
    for i in allpkgs:
        with open("/etc/car/packagelist", "a") as f:
            f.write(i+"\n")
