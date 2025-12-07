from status import status

def main(package):
    with open("/etc/car/packagelist", "r") as f:
        packages = f.read()

    packagelist = packages.splitlines()

    if package in packagelist:
        return True
    else:
        status("Package not found.", "error")
        print("Maybe you forgot to update your packagelist?")
        print("     car updatelist")
