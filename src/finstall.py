import install


def main(packages, noconfirm=False):
    for i in packages:
        install.main(i, noconfirm)
