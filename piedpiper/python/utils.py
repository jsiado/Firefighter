#!/usr/bin/env python
from __future__ import print_function
import os
import subprocess
from Firefighter.piedpiper.template import *


def floatpfy(f):
    ''' Given a float, return its string with . replaced with p'''

    if int(f)-f:
        return str(f).replace('.', 'p')
    else:
        return str(int(f))

def get_param_from_gridpackname(gpname):
    '''
    infer parameters to generate the gridpack
    e.g. SIDM_BsTo2DpTo2Mu2e_MBs-1000_MDp-1p2_ctau-9p6_slc6_amd64_gcc481_CMSSW_7_1_30_tarball.tar.xz
    returns (mbs, mdp, ctau)
    '''

    params = [x for x in gpname.split('_') if '-' in x]
    mbs, mdp, ctau = None, None, None
    for p in params:
        if 'MBs' in p:
            mbs = float(p.split('-')[-1].replace('p', '.'))
        if 'MDp' in p:
            mdp = float(p.split('-')[-1].replace('p', '.'))
        if 'ctau' in p:
            ctau = float(p.split('-')[-1].replace('p', '.'))

    if not all([mbs, mdp, ctau]):
        print('Cannot infer from gridpack name: "{0}"'.format(gpname))

    return (mbs, mdp, ctau)


def get_param_from_dataset(ds):
    '''
    infer parameters from signal MC dataset name
    e.g. /SIDM_XXTo2ATo4Mu/wsi-mXX-200_mA-5_ctau-187p5_GENSIM_2016-ce4b469d5a8a6c79b1702c0e107219c7/USER
    returns (mxx, ma, ctau)
    '''

    nametag = ds.split('/')[-2]
    paramstring = nametag.split('-', 1)[-1].rsplit('/', 1)[0]
    paramtuple = [s for s in paramstring.split('_') if '-' in s]
    mxx, ma, ctau = None, None, None
    for p in paramtuple:
        if 'mXX' in p:
            mxx = float(p.split('-')[-1].replace('p', '.'))
        if 'mA' in p:
            ma = float(p.split('-')[-1].replace('p', '.'))
        if 'ctau' in p:
            ctau = float(p.split('-')[-1].replace('p', '.'))

    if not all([mxx, ma, ctau]):
        print('Cannot infer from dataset name: "{0}"'.format(ds))

    return (mxx, ma, ctau)


def get_nametag_from_dataset(dataset):
    '''
    infer nametag from a dataset string
    e.g.: /CRAB_PrivateMC/wsi-SIDM_BsTo2DpTo4Mu_MBs-200_MDp-1p2_ctau-0p48-354cda32a6a404e25b0eb21bb1bef952/USER

    returns SIDM_BsTo2DpTo4Mu_MBs-200_MDp-1p2_ctau-0p48
    '''

    return dataset.split('/')[-2].split('-', 1)[-1].rsplit('-', 1)[0]


def check_voms_valid():
    '''
    check if certificate is expired
    '''

    cmd = 'voms-proxy-info -file /tmp/x509up_u{0} -timeleft'.format(os.getuid())
    p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
    if p[0] and not p[1]:
        return True
    else:
        return False


def get_voms_certificate():
    '''
    make sure VOMS certificate is valid
    '''

    if not check_voms_valid():
        os.system('voms-proxy-init -voms cms -valid 192:00')

def get_gentemplate(year):
    ''' return the gen fragmeent in template.py, adjust if necessary '''

    if int(year)==2016:
        return '\n'.join([l for l in genTemplate.split('\n') if 'CP5Settings' not in l])
    else:
        return genTemplate

def get_command(step, year):

    if step.upper() not in ['GEN-SIM', 'PREMIX-RAW-HLT', 'AODSIM'] \
        or str(year) not in ['2016', '2017', '2018']:
        print('Unsupported parameter for get_command(step, year):')
        print('-- step: {0}'.format(step))
        print('-- year: {0}'.format(year))
        sys.exit()

    step = step.upper()
    year = str(year)

    cmd = ''
    cfgOutput = os.path.join(os.environ['CMSSW_BASE'], 'src', 'Firefighter', 'piedpiper', 'cfg')

    if step == 'GEN-SIM':

        cfgOutput = os.path.join(cfgOutput, 'SIDM_GENSIM_cfg.py')

        if year == '2016':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'Firefighter/piedpiper/python/externalLHEProducer_and_PYTHIA8_Hadronizer_cff.py',
                    '--fileout file:SIDM_GENSIM.root',
                    '--mc',
                    '-s LHE,GEN,SIM',
                    '--era Run2_{0}',
                    '--nThreads 4',
                    '--conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6',
                    '--beamspot Realistic50ns13TeVCollision',
                    '--datatier GEN-SIM',
                    '--eventcontent RAWSIM',
                    '-n 10',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

        else:

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'Firefighter/piedpiper/python/externalLHEProducer_and_PYTHIA8_Hadronizer_cff.py',
                    '--fileout file:SIDM_GENSIM.root',
                    '--mc',
                    '-s LHE,GEN,SIM',
                    '--era Run2_{0}',
                    '--nThreads 4',
                    '--conditions auto:phase1_{0}_realistic',
                    '--beamspot Realistic25ns13TeVEarly{0}Collision',
                    '--datatier GEN-SIM',
                    '--eventcontent RAWSIM',
                    '-n 10',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

    if step == 'PREMIX-RAW-HLT':

        cfgOutput = os.path.join(cfgOutput, 'SIDM_PREMIXRAWHLT_cfg.py')

        if year == '2016':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step1',
                    '--filein file:SIDM_GENSIM.root',
                    '--fileout file:SIDM_PREMIXRAWHLT.root',
                    '--mc',
                    '-s DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:@relval{0}',
                    '--era Run2_{0}',
                    '--nThreads 4',
                    '--conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6',
                    '--datatier GEN-SIM-RAW',
                    '--eventcontent PREMIXRAW',
                    '--datamix PreMix',
                    '-n -1',
                    '--pileup_input "dbs:/Neutrino_E-10_gun/RunIISpring15PrePremix-PUMoriond17_80X_mcRun2_asymptotic_2016_TrancheIV_v2-v2/GEN-SIM-DIGI-RAW"',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'

                ]
            ).format(year, cfgOutput)

        elif year == '2017':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step1',
                    '--filein file:SIDM_GENSIM.root',
                    '--fileout file:SIDM_PREMIXRAWHLT.root',
                    '--mc',
                    '-s DIGIPREMIX_S2,DATAMIX,L1,DIGI2RAW,HLT:@relval{0}',
                    '--era Run2_{0}',
                    '--nThreads 8',
                    '--conditions auto:phase1_{0}_realistic',
                    '--beamspot Realistic25ns13TeVEarly{0}Collision',
                    '--datatier GEN-SIM-RAW',
                    '--eventcontent PREMIXRAW',
                    '--datamix PreMix',
                    '-n -1',
                    '--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-MCv2_correctPU_94X_mc2017_realistic_v9-v1/GEN-SIM-DIGI-RAW"',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

        elif year == '2018':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step1',
                    '--filein file:SIDM_GENSIM.root',
                    '--fileout file:SIDM_PREMIXRAWHLT.root',
                    '--mc',
                    '-s DIGI,DATAMIX,L1,DIGI2RAW,HLT:@relval{0}',
                    '--procModifiers premix_stage2',
                    '--era Run2_{0}',
                    '--nThreads 8',
                    '--conditions auto:phase1_{0}_realistic',
                    '--beamspot Realistic25ns13TeVEarly{0}Collision',
                    '--datatier GEN-SIM-RAW',
                    '--eventcontent PREMIXRAW',
                    '--geometry DB:Extended',
                    '--datamix PreMix',
                    '-n -1',
                    '--pileup_input "dbs:/Neutrino_E-10_gun/RunIISummer17PrePremix-PUFull18_102X_upgrade2018_realistic_v11-v1/GEN-SIM-DIGI-RAW"',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

    if step == 'AODSIM':

        cfgOutput = os.path.join(cfgOutput, 'SIDM_AODSIM_cfg.py')

        if year == '2016':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step2',
                    '--filein file:SIDM_PREMIXRAWHLT.root',
                    '--fileout file:SIDM_AODSIM.root',
                    '--mc',
                    '--runUnscheduled',
                    '-s RAW2DIGI,RECO,EI',
                    '--era Run2_{0}',
                    '--nThreads 4',
                    '--conditions 80X_mcRun2_asymptotic_2016_TrancheIV_v6',
                    '--datatier AODSIM',
                    '--eventcontent AODSIM',
                    '-n -1',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

        elif year == '2017':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step2',
                    '--filein file:SIDM_PREMIXRAWHLT.root',
                    '--fileout file:SIDM_AODSIM.root',
                    '--mc',
                    '--runUnscheduled',
                    '-s RAW2DIGI,RECO,EI',
                    '--era Run2_{0}',
                    '--nThreads 8',
                    '--conditions auto:phase1_{0}_realistic',
                    '--datatier AODSIM',
                    '--eventcontent AODSIM',
                    '-n -1',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

        elif year == '2018':

            cmd = ' '.join(
                [
                    'cmsDriver.py',
                    'step2',
                    '--filein file:SIDM_PREMIXRAWHLT.root',
                    '--fileout file:SIDM_AODSIM.root',
                    '--mc',
                    '--runUnscheduled',
                    '-s RAW2DIGI,L1Reco,RECO,RECOSIM,EI',
                    '--procModifiers premix_stage2',
                    '--era Run2_{0}',
                    '--nThreads 8',
                    '--conditions auto:phase1_{0}_realistic',
                    '--datatier AODSIM',
                    '--eventcontent AODSIM',
                    '-n -1',
                    '--no_exec',
                    '--python_filename {1}',
                    '--customise Configuration/DataProcessing/Utils.addMonitoring'
                ]
            ).format(year, cfgOutput)

    print("><><><>Output python cfg file: {}".format(cfgOutput))
    return cmd