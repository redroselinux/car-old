def main():
    # open repro.car
    with open("/etc/repro.car", "r") as f:
        repro = f.read()

    # sometimes, car writes the same package multiple times. for this reason,
    # do not only print content but filter specifically the PACKAGES from the file
    alr_used = []
    for i in repro.splitlines():
        if i in alr_used:
            # already printed, continue
            continue
        # we have used this just now, write it into alr_used
        alr_used.append(i)

        # print the current package
        print(i)
