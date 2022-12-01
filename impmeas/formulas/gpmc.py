import os
import re
from .utils import cnf2dimacs

class GPMC:
    def __init__(self, 
        src = "/usr/local/bin/gpmc", 
        tmp_filename = "/tmp/dimacs.cnf",
        bj=True, cs=3500):
        self.__solver_dir = "/".join(src.split("/")[:-1])
        self.__solver_name = src.split("/")[-1]
        self.__tmp_filename = tmp_filename
        self.__bj = bj
        self.__cs = cs 

    def satcount_file(self, cnf_file, debug=False):
        cnf_file_abs = os.path.abspath(cnf_file)
        file_content = open(cnf_file, "r").read().split("\n")
        mode = "2" if "c t pmc" in file_content else "0"
        command =  f'''
            cd {self.__solver_dir} && 
            {self.__solver_dir}/{self.__solver_name} {'-bj' if self.__bj else '-no-bj'} -cs={self.__cs} -mode={mode} {cnf_file_abs}
        '''
        ret = os.popen(command).read()
        if debug: print(ret)
        satcount = int(float(re.findall(r"c s exact arb int (.*)", ret)[0]))
        return satcount 

    def satcount(self, cnf: list[list[int]], \
                 debug=False, exists=set()):
        with open(self.__tmp_filename, "w") as fw:
            nr_vars = max(max(abs(lit) for lit in cl) for cl in cnf)
            all_vars = set(range(1, nr_vars+1))
            dimacs = cnf2dimacs(cnf, projected=all_vars-exists)
            fw.write(dimacs)
        value = self.satcount_file(self.__tmp_filename, debug=debug)
        os.remove(self.__tmp_filename)
        return value

 