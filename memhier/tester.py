import sys
import random

def genString(x, l) -> list:

    trace = []

    while len(trace) < l:
        rw = 'R'
        num = random.getrandbits(x)
        if random.randint(0, 1):
            rw = "W"

        string = f"{rw}:{hex(num)[2:]}\n"

        trace.append(string)

    return trace

if __name__ == "__main__":
    trace = genString(int(sys.argv[1]), int(sys.argv[2]))
    with open("test.dat", "w") as writefile:
        writefile.writelines(trace)