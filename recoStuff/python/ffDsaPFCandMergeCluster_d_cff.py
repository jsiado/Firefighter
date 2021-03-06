import FWCore.ParameterSet.Config as cms
import FWCore.ParameterSet as fps

from Firefighter.recoStuff.ffDsaPFCandMergeCluster_cff import *
from Firefighter.recoStuff.HLTFilter_cfi import hltfilter

import os
import sys

cmsrel = os.environ["CMSSW_VERSION"]

if cmsrel.startswith("CMSSW_8"):
    year = 2016
elif cmsrel.startswith("CMSSW_9"):
    year = 2017
elif cmsrel.startswith("CMSSW_10"):
    year = 2018
else:
    sys.exit("Wrong release! Not in the year of [2016, 2017, 2018]")

if year == 2016:
    hltfilter.TriggerPaths = cms.vstring(
        "HLT_L2DoubleMu28_NoVertex_2Cha_Angle2p5_Mass10",
        "HLT_L2DoubleMu38_NoVertex_2Cha_Angle2p5_Mass10",
    )
if year == 2017:
    hltfilter.TriggerPaths = cms.vstring(
        "HLT_TrkMu12_DoubleTrkMu5NoFiltersNoVtx",
        "HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx",
    )
if year == 2018:
    hltfilter.TriggerPaths = cms.vstring(
        "HLT_DoubleL2Mu23NoVtx_2Cha",
        "HLT_DoubleL2Mu23NoVtx_2Cha_NoL2Matched",
        "HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed",
        "HLT_DoubleL2Mu23NoVtx_2Cha_CosmicSeed_NoL2Matched",
        "HLT_DoubleL2Mu25NoVtx_2Cha_Eta2p4",
        "HLT_DoubleL2Mu25NoVtx_2Cha_CosmicSeed_Eta2p4",
    )

# ffLeptonJetSeq._seq._collection.insert(0, hltfilter)
ffLeptonJetSeq.insert(0, hltfilter)


def _isModule(m):
    return isinstance(m, fps.Modules._Module)


def _isSequence(s):
    return isinstance(s, fps.SequenceTypes.Sequence)


def removeModuleFromSeq(seq, cond):
    for _m in seq._seq._collection:
        if _isModule(_m) and cond(_m):
            seq.remove(_m)
        elif _isSequence(_m):
            if _m._seq:
                removeModuleFromSeq(_m, cond)


removeMCMods = lambda m: m.type_().startswith("MC")

# print ffLeptonJetSeq.dumpSequencePython()
removeModuleFromSeq(ffLeptonJetSeq, removeMCMods)
