#!/usr/bin/env python
from __future__ import print_function
import os
import yaml
import time

from Firefighter.piedpiper.utils import *

from crabConfig import *

doCmd = True
CONFIG_NAME = 'multicrabConfig.yml'


def main():

    # safety check
    if os.environ['CMSSW_BASE'] not in os.path.abspath(__file__):
        print('$CMSSW_BASE: ', os.environ['CMSSW_BASE'])
        print('__file__: ', os.path.abspath(__file__))
        sys.exit('Inconsistant release environment!')
    
    # load config
    multiconf = yaml.load(open(CONFIG_NAME).read())

    datasets = multiconf['aodsimdatasets']
    year     = multiconf['year']
    config.Data.outLFNDirBase += '/{0}'.format(year)

    donelist = list()
    for ds in datasets:

        nametag = get_nametag_from_dataset(ds)
        print("dataset: ", ds)
        print("nametag: ", nametag)
        config.Data.inputDataset = ds
        config.Data.outputDatasetTag = nametag
        config.General.requestName = '_'.join([
            getUsernameFromSiteDB(),
            'ffNtuple',
            str(year),
            nametag,
            time.strftime('%y%m%d-%H%M%S')
        ])

        if doCmd:
            from CRABAPI.RawCommand import crabCommand
            crabCommand('submit', config = config)
            time.sleep(5)
            donelist.append(ds)

    print('submitted: ', len(donelist))
    for x in donelist: print(x)
    print('------------------------------------------------------------')

    undonelist = [x for x in inputdatasets if x not in donelist]
    print('unsubmitted: ', len(undonelist))
    for x in undonelist: print(x)
    if undonelist:
        with open('unsubmitted.yml.log', 'w') as outf:
            yaml.dump({'aodsimdatasets': undonelist, 'year': year}, outf, default_flow_style=False)


if __name__ == '__main__':
    main()