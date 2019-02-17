#!/usr/bin/env python
from __future__ import print_function

import os
import sys
import yaml
import time

from CRABAPI.RawCommand import crabCommand
from Firefighter.piedpiper.utils import ffDataset, adapt_config_with_dataset
from crabConfig import config, year


doCmd = True
CONFIG_NAME = sys.argv[1]


def main():

    # safety check
    if os.environ['CMSSW_BASE'] not in os.path.abspath(__file__):
        print('$CMSSW_BASE: ', os.environ['CMSSW_BASE'])
        print('__file__: ', os.path.abspath(__file__))
        sys.exit('Inconsistant release environment!')

    # load config
    multiconf = yaml.load(open(CONFIG_NAME).read())

    datasets = multiconf['aodsimdatasets']

    donelist = list()
    for ds in datasets:

        thisData = ffDataset(ds, year)
        config = adapt_config_with_dataset(config, thisData)

        if doCmd:
            crabCommand('submit', config=config)
            donelist.append(ds)

    print('submitted: {}'.format(len(donelist)), *donelist, sep='\n')
    print('------------------------------------------------------------')

    undonelist = [x for x in datasets if x not in donelist]
    print('unsubmitted: {}'.format(len(undonelist)), *undonelist, sep='\n')

    if undonelist:
        with open('unsubmitted.yml.log', 'w') as outf:
            yaml.dump({'aodsimdatasets': undonelist, 'year': year},
                      outf, default_flow_style=False)


if __name__ == '__main__':
    main()
