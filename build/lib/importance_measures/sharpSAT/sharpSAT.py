import os
import re
from . import Formula

def cnf2dimacs(cnf):
    # example output:
    # '''
    #     p cnf 3 2
    #     c t mc
    #     1 2 -3 0
    #     -2 3 0
    # '''
    # represents the CNF (x1 & x2 & ~x3) | (~x2 & x3)
    nr_vars = max(max(map(abs, clause)) for clause in cnf)
    ret = f"p cnf {nr_vars} {len(cnf)}\n"
    ret += "c t mc\n"
    for cl in cnf: 
        ret += " ".join(map(str, cl)) + " 0\n"
    return ret

class SharpSAT:
    def __init__(self, 
        src = "/usr/local/bin/sharpSAT", 
        tmp_filename = "/tmp/dimacs.cnf",
        decot=1, decow=100, tmpdir="/tmp", cs=3500):
        self.__solver_dir = "/".join(src.split("/")[:-1])
        self.__solver_name = src.split("/")[-1]
        self.__tmp_filename = tmp_filename
        self.__args = { "decot": decot, "decow": decow, "tmpdir": tmpdir, "cs": cs } 

    def satcount_file(self, cnf_file, debug=False):
        cnf_file_abs = os.path.abspath(cnf_file)
        opt_args = " ".join(f"-{key} {arg}" for key, arg in self.__args.items())
        command =  f'''
            cd {self.__solver_dir} && 
            {self.__solver_dir}/{self.__solver_name} -WE {opt_args} {cnf_file_abs}
        '''
        ret = os.popen(command).read()
        if debug: print(ret)
        satcount = int(float(re.findall(r"c s exact arb float (.*)", ret)[0]))
        return satcount 

    def satcount(self, cnf, debug=False):
        if isinstance(cnf, Formula):
            cnf, _ = cnf.cnf
        with open(self.__tmp_filename, "w") as fw:
            fw.write(cnf2dimacs(cnf))
        value = self.satcount_file(self.__tmp_filename, debug=debug)
        os.remove(self.__tmp_filename)
        return value

if __name__ == "__main__":
    f = Formula.parse("~x1 & (x2 | x3)") & Formula.parse("~x4")
    ssat = SharpSAT()
    result_tseytin = ssat.satcount(f, debug=False)
    result_hand_coded = ssat.satcount([[-1], [2,3], [-4]], debug=False)
    print(f"satcount of f={f} via tseytin transformation: {result_tseytin}")
    print(f"satcount of hand-coded cnf: {result_hand_coded}")
    print(f"variables in f: {f.vars}")
    print(f"cofactor wrt x2 = 1: {f.cofactor('x2', True)}")
 