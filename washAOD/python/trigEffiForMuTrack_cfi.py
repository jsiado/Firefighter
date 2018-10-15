import FWCore.ParameterSet.Config as cms

trigEffiForMuTrack = cms.EDAnalyzer('trigEffiForMuTrack',
    muTrack = cms.InputTag("displacedStandAloneMuons"),
    genParticle = cms.InputTag("genParticles"),
    trigResult = cms.InputTag("TriggerResults","","HLT"),
    trigEvent = cms.InputTag("hltTriggerSummaryAOD","","HLT"),
    trigPath = cms.vstring('HLT_TrkMu16_DoubleTrkMu6NoFiltersNoVtx'),
    processName = cms.string('HLT'),
    nMuons = cms.int32(2)
  )
