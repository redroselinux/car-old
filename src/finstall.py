import os

import install


def main(packages, noconfirm=False):
    file_mode = False
    for i in packages:
        if i == ".file":
            file_mode = True
            continue  # skip ".file" itself
        elif i == ".pkg":
            file_mode = False
            continue  # skip ".pkg" itself

        if file_mode:
            with open(i, "r") as f:
                config = f.read()

            for j in config.splitlines():
                if j.startswith("get"):
                    args = j.split()
                    if "--noconfirm" in args:
                        args.remove("--noconfirm")
                        noconfirm = True
                    for k in args[1:]:  # skip "get"
                        install.main(k, noconfirm)
                    noconfirm = False
                else:
                    os.system(j)
            continue  # don’t call install.main on the file itself

        # normal install
        install.main(i, noconfirm)
