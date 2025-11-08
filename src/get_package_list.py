from status import status
import os

def main(package):
    with open("/home/"+os.getlogin()+"/.config/car/packagelist", "r") as f:
        packages = f.read()

    packagelist = packages.splitlines()

    if package in packagelist:
        return True
    else:
        status("Package not found.", "error")
        print("Maybe you forgot to update your packagelist?")
        print("     car updatelist")
    
