
from CRABClient.UserUtilities import config, getUsernameFromSiteDB
config = config()

import time
config.General.requestName = 'wsiLJGun_%s' % time.strftime('%y%m%d-%H%M%S')
config.General.workArea = 'crabWorkArea'
config.General.transferOutputs = True
config.General.transferLogs = True

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = '../cfg/ljGun_AODSIM_cfg.py'
config.JobType.numCores = 8
config.JobType.maxMemoryMB = 6000
config.JobType.disableAutomaticOutputCollection = False

config.Data.inputDataset = '/CRAB_PrivateMC/wsi-LJGunMuMu-51747e2edb4a043113c6d615634bafea/USER'
config.Data.inputDBS = 'phys03'
config.Data.splitting = 'FileBased'
config.Data.unitsPerJob = 1
config.Data.outLFNDirBase = '/store/user/%s/MCLJGun' % (getUsernameFromSiteDB())
config.Data.publication = True
config.Data.outputDatasetTag = 'LJGunMuMu'
config.Data.ignoreLocality = True

config.Site.whitelist = ['T3_US_FNALLPC', 'T2_CH_CERN', 'T2_US_Purdue']
config.Site.ignoreGlobalBlacklist = True
config.Site.storageSite = 'T3_US_FNALLPC'
