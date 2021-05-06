import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet.VarParsing as VarParsing

import os
import yaml
from os.path import join
from Firefighter.ffConfig.ffChainConstruction import customizeNtupleTrigger

options = VarParsing.VarParsing("analysis")
configDefault = join(
    os.getenv("CMSSW_BASE"), "src/Firefighter/ffConfig/cfg/ffSuperConfig.yml"
)
options.register(
    "config",
    configDefault,
    VarParsing.VarParsing.multiplicity.singleton,
    VarParsing.VarParsing.varType.string,
    "Path to ffSuperConfig.yml",
)
# options.register(
#     "keepskim",
#     0,
#     VarParsing.VarParsing.multiplicity.singleton,
#     VarParsing.VarParsing.varType.int,
#     "Whether to keep skim output.",
# )
options.parseArguments()
ffConfig = yaml.safe_load(open(options.config))


process = cms.Process("FFNTP")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.load("Configuration.StandardSequences.Services_cff")
process.load("Configuration.EventContent.EventContent_cff")
process.load("Configuration.StandardSequences.GeometryRecoDB_cff")
process.load("Configuration.StandardSequences.EndOfProcess_cff")
process.load("Configuration.StandardSequences.MagneticField_38T_cff")
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_condDBv2_cff")
process.GlobalTag.globaltag = ffConfig["condition-spec"]["globalTag"]

process.MessageLogger.cerr.threshold = cms.untracked.string("INFO")
process.MessageLogger.cerr.FwkReport.reportEvery = cms.untracked.int32(
    ffConfig["job-spec"]["reportEvery"]
)

process.options = cms.untracked.PSet(
    wantSummary=cms.untracked.bool(True),
    numberOfThreads=cms.untracked.uint32(ffConfig["job-spec"]["numThreads"]),
    numberOfStreams=cms.untracked.uint32(0),
)

process.maxEvents = cms.untracked.PSet(
    input=cms.untracked.int32(ffConfig["data-spec"]["maxEvents"])
)

process.source = cms.Source(
    "PoolSource",
    fileNames=cms.untracked.vstring(*ffConfig["data-spec"]["inputFileList"]),
)
if ffConfig["data-spec"].get("lumiMask", None):
    import FWCore.PythonUtilities.LumiList as LumiList

    process.source.lumisToProcess = LumiList.LumiList(
        url=ffConfig["data-spec"]["lumiMask"]
    ).getVLuminosityBlockRange()

process.TFileService = cms.Service(
    "TFileService",
    fileName=cms.string(ffConfig["data-spec"]["outputFileName"]),
    closeFileFast=cms.untracked.bool(True),
)


preTriggerPaths=cms.vstring(
    "HLT_IsoMu24",
    "HLT_Mu50",
)

triggerPaths=cms.vstring(
    # L2DoubleMu triggers
    "HLT_DoubleL2Mu23NoVtx_2Cha",
    "HLT_DoubleL2Mu23NoVtx_2Cha_NoL2Matched",
    "HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed",
    "HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed_NoL2Matched",
    "HLT_DoubleL2Mu25NoVtx_2Cha",
    "HLT_DoubleL2Mu25NoVtx_2Cha_NoL2Matched",
    "HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed",
    "HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_NoL2Matched",
    "HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4",
    "HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4",

    # mu photon trigger
    "HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL",

    # single mu trigger
    "HLT_IsoMu24",
    "HLT_Mu50",

    # single electron trigger
    "HLT_Ele28_WPTight_Gsf",

    # tri- muon trigger
    "HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx",

    #newTRG for 2021-may study
    #Double Muon
    "HLT_DoubleL2Mu30NoVtx_2Cha_CosmicSeed_Eta2p4"
    "HLT_DoubleL2Mu30NoVtx_2Cha_Eta2p4"
    "HLT_DoubleMu33NoFiltersNoVtxDisplaced"
    "HLT_DoubleMu40NoFiltersNoVtxDisplaced"
    "HLT_DoubleMu43NoFiltersNoVtx"
    "HLT_DoubleMu48NoFiltersNoVtx"

    #Muon EG triggers
    "HLT_DiMu4_Ele9_CaloIdL_TrackIdL_DZ_Mass3p8"
    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ"
    "HLT_DiMu9_Ele9_CaloIdL_TrackIdL"
    "HLT_DoubleMu20_7_Mass0to30_L1_DM4EG"
    "HLT_DoubleMu20_7_Mass0to30_L1_DM4"
    "HLT_DoubleMu20_7_Mass0to30_Photon23"
    "HLT_Mu12_DoublePhoton20"
    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ"
    "HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL"
    "HLT_Mu17_Photon30_IsoCaloId"
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ"
    "HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL"
    "HLT_Mu27_Ele37_CaloIdL_MW"
    "HLT_Mu37_Ele27_CaloIdL_MW"
    "HLT_Mu38NoFiltersNoVtxDisplaced_Photon38_CaloIdL"
    "HLT_Mu43NoFiltersNoVtxDisplaced_Photon43_CaloIdL"
    "HLT_Mu43NoFiltersNoVtx_Photon43_CaloIdL"
    "HLT_Mu48NoFiltersNoVtx_Photon48_CaloIdL"
    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL_DZ"
    "HLT_Mu8_DiEle12_CaloIdL_TrackIdL"
    "HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350_DZ"
    "HLT_Mu8_Ele8_CaloIdM_TrackIdM_Mass8_PFHT350"

    #Single Muon
    "HLT_L1SingleMu18"
    "HLT_L1SingleMu25"
    "HLT_L2Mu10"
    "HLT_L2Mu50"
    
    #Egamma
    "HLT_Photon100EBHE10"
    "HLT_Photon100EB_TightID_TightIso"
    "HLT_Photon100EEHE10"
    "HLT_Photon100EE_TightID_TightIso"
    "HLT_Photon110EB_TightID_TightIso"
    "HLT_Photon120EB_TightID_TightIso"
    "HLT_Photon120_R9Id90_HE10_IsoM"
    "HLT_Photon120"
    "HLT_Photon150"
    "HLT_Photon165_R9Id90_HE10_IsoM"
    "HLT_Photon175"
    "HLT_Photon200"
    "HLT_Photon20_HoverELoose"
    "HLT_Photon300_NoHE"
    "HLT_Photon30_HoverELoose"
    "HLT_Photon33"
    "HLT_Photon50_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3_PFMET50"
    "HLT_Photon50_R9Id90_HE10_IsoM"
    "HLT_Photon50"
    "HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL_PFHT350MinPFJet15"
    "HLT_Photon60_R9Id90_CaloIdL_IsoL_DisplacedIdL"
    "HLT_Photon60_R9Id90_CaloIdL_IsoL"
    "HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ300_PFJetsMJJ400DEta3"
    "HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_CaloMJJ400_PFJetsMJJ600DEta3"
    "HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ300DEta3"
    "HLT_Photon75_R9Id90_HE10_IsoM_EBOnly_PFJetsMJJ600DEta3"
    "HLT_Photon75_R9Id90_HE10_IsoM"
    "HLT_Photon75"
    "HLT_Photon90_R9Id90_HE10_IsoM"
    "HLT_Photon90"
)

triggerObjFilterLabels=cms.vstring(
    # L2 DoubleMu triggers
    "hltL2DoubleMu23NoVertexL2Filtered2Cha",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx23Q2ChaNoL2Matched",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx23Q2ChaCosmicSeed",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx23Q2ChaCosmicSeedNoMatched",
    "hltL2DoubleMu25NoVtxFiltered2Cha",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx25Q2ChaNoL2Matched",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx25Q2ChaCosmicSeed",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx25Q2ChaCosmicSeedNoMatched",
    "hltL2DoubleMu25NoVtxFiltered2ChaEta2p4",
    "hltL2fL1sMuORL1f0DoubleL2NoVtx25Q2ChaCosmicSeedEta2p4",

    "hltL1sDoubleMu125to157ORTripleMu444",
    "hltL1sDoubleMu125to157ORTripleMu444ORSingleMu22",

    # mu photon trigger
    "hltMu38NoFiltersNoVtxPhoton38CaloIdLHEFilter",
    "hltL3fL1sMu5EG20orMu20EG15L1f5L2NVf16L3NoFiltersNoVtxFiltered38Displaced",
    "hltL1sMu5EG23IorMu7EG23IorMu20EG17IorMu23EG10",
    "hltEGL1Mu5EG20Filter",

    # single mu trigger
    "hltL3crIsoL1sSingleMu22L1f0L2f10QL3f24QL3trkIsoFiltered0p07",
    "hltL1sSingleMu22",
    "hltL3fL1sMu22Or25L1f0L2f10QL3Filtered50Q",
    "hltL1sSingleMu22or25",

    # single electron trigger
    "hltEle28WPTightGsfTrackIsoFilter",
    "hltEGL1SingleEGOrFilter",

    # tri- muon trigger
    "hltL3fL1sDoubleMu155ORTripleMu444L1f0L2f10OneMuL3Filtered16NoVtx",
    "hltL1sDoubleMu125to157ORTripleMu444",
)


process = customizeNtupleTrigger( process, ffConfig,
                                preTriggerPaths=preTriggerPaths,
                                triggerPaths=triggerPaths,
                                triggerObjFilterLabels=triggerObjFilterLabels
                                )

# print process.dumpPython().replace('\n\n','')
