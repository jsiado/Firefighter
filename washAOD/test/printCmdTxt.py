#!/usr/bin/env python
from __future__ import print_function
import os

year = 2017
frag = 'jetMassSculpt'
suffixTag = '100k' # [100k, Pythia, PythiaTest2]

def main():

    print()
    print("#"*79)
    print("YEAR = ", year)
    print("FRAG = ", '%s_cfg.py'%frag)
    print("#"*79)
    print()

    ctaus = ['1p20e-03', '0p012', '0p12', '0p6', '1p2', '3p6']
    for c in ctaus:
        datalistF = 'SIDMmumu_Mps-200_MZp-1p2_ctau-{0}'.format(c)
        if suffixTag:
            datalistF = '_'.join([datalistF, suffixTag])
        if not os.path.isfile('../data/{0}/{1}.list'.format(year, datalistF)): continue
        print("nohup ./mkNtuple.sh {0} {1} {2} &".format(datalistF, frag, year))

if __name__ == '__main__':
    main()