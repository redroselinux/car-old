from status import status

def main(package):
    with open("/etc/car/packagelist", "r") as f:
        packages = f.read()

    packagelist = packages.splitlines()

    # packagelist has "repo/pkg" format; package is always short name
    if package in packagelist:
        return True
    if any(pkg.split("/", 1)[-1] == package for pkg in packagelist if pkg.strip()):
        return True
    status("Package not found.", "error")
    print("Maybe you forgot to update your packagelist?")
    print("     car updatelist")
