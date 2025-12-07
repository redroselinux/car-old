import os

def main():
    with open("/etc/repro.car", "r") as f:
        repro = f.read()

    alr_used = []
    for i in repro.splitlines():
        if i in alr_used: continue
        alr_used.append(i)

        print(i)
