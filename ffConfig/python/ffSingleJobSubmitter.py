#!/usr/bin/env python
"""submit job for a single dataset
"""
from __future__ import print_function

import importlib
import os
import sys
from os.path import join

import yaml


# tosubd_ = "Firefighter.ffConfig.production.Autumn18.data.DoubleMuon_Run2018A"
# tosubd_ = "Firefighter.ffConfig.production.Autumn18.bkgmc.TTJets_TuneCP5_13TeV-madgraphMLM-pythia8"
tosubd_ = join(os.getenv('CMSSW_BASE'),
               "src/Firefighter/ffConfig/python/production/Autumn18/sigmc/private/",
               "XXTo2ATo4Mu_mXX-500_mA-1p2_ctau-18.yml")
print(tosubd_)


def main():
    tosubdff = yaml.load(open(tosubd_), Loader=yaml.Loader)

    from Firefighter.ffConfig.crabConfigBuilder import configBuilder

    cb = configBuilder(tosubdff, eventRegion="all")
    for c in cb.build():
        configBuilder.submit(c)

    # from Firefighter.ffConfig.condorConfigBuilder import configBuilder
    # from Firefighter.piedpiper.utils import get_voms_certificate

    # os.system(
    #    "tar -X EXCLUDEPATTERNS --exclude-vcs -zcf `basename ${CMSSW_BASE}`.tar.gz -C ${CMSSW_BASE}/.. `basename ${CMSSW_BASE}`"
    # )
    # get_voms_certificate()

    # cb = configBuilder(tosubdff, eventRegion="all")
    # for c in cb.build():
    #     configBuilder.submit(c)


if __name__ == "__main__":
    print('='*79, 'WARNING deprecated! consider switch to `ffBatchJobSubmitter_v2.py`', '='*79, sep='\n')
    sys.exit('Bye!')
    print(" I am Mr. ffSingleJobSubmitter ".center(79, '+'))
    main()
