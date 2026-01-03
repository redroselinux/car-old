import mirrors


def main(package):
    # get list of packages
    packages = mirrors.fetch_all_packages(mirrors.packagelist_places)

    # loop through the packages
    for i in packages:
        # found, print it
        if package in i:
            print(i)
