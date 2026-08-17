import gdb
import math



class DumpMem(gdb.Command):
    """dumpmem PTR N [FILE]"""

    def __init__(self):
        super().__init__("dumpmem", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        if len(argv) < 2:
            print("Usage: dumpmem PTR N [FILE]")
            return

        ptr = gdb.parse_and_eval(argv[0])
        n = int(gdb.parse_and_eval(argv[1]))

        out = open(argv[2], "w") if len(argv) > 2 else None

        for i in range(n):
            val = float(ptr[i])
            line = f"{i:8d} {val:.17e}"
            if out:
                out.write(line + "\n")
            else:
                print(line)

        if out:
            out.close()



class CompareVec(gdb.Command):
    """comparevec FILE1 FILE2 [TOL]

Compare two files produced by dumpmem.
Default tolerance is 1e-3.
"""

    def __init__(self):
        super().__init__("comparevec", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        if len(argv) < 2:
            print("Usage: comparevec FILE1 FILE2 [TOL]")
            return

        file1 = argv[0]
        file2 = argv[1]
        tol = float(argv[2]) if len(argv) >= 3 else 1e-3

        with open(file1) as f:
            a = f.readlines()

        with open(file2) as f:
            b = f.readlines()

        if len(a) != len(b):
            print(f"Length mismatch: {len(a)} vs {len(b)}")
            return

        ndiff = 0
        maxdiff = 0.0
        maxidx = -1

        for i, (la, lb) in enumerate(zip(a, b)):
            va = float(la.split()[1])
            vb = float(lb.split()[1])

            diff = abs(va - vb)

            if diff > maxdiff:
                maxdiff = diff
                maxidx = i

            if diff > tol:
                if ndiff == 0:
                    print("Differences:")
                print(f"{i:8d}  {va:.17e}  {vb:.17e}  diff={diff:.3e}")
                ndiff += 1

        if ndiff == 0:
            print(f"Vectors agree within tolerance {tol:g}")
        else:
            print()
            print(f"{ndiff} entries differ (tol={tol:g})")
            print(f"Maximum difference: {maxdiff:.3e} at index {maxidx}")

class VecNorm(gdb.Command):
    """vecnorm FILE"""

    def __init__(self):
        super().__init__("vecnorm", gdb.COMMAND_DATA)

    def invoke(self, arg, from_tty):
        argv = gdb.string_to_argv(arg)

        if len(argv) != 1:
            print("Usage: vecnorm FILE")
            return

        s = 0.0
        n = 0

        with open(argv[0]) as f:
            for line in f:
                val = float(line.split()[1])
                s += val * val
                n += 1

        print(f"L2 norm = {math.sqrt(s):.17e}")
        print(f"Entries = {n}")

VecNorm()
DumpMem()
CompareVec()

