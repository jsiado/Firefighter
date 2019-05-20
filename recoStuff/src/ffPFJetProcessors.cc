#include "Firefighter/recoStuff/interface/ffPFJetProcessors.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "Firefighter/recoStuff/interface/RecoHelpers.h"
#include "TrackingTools/Records/interface/TransientTrackRecord.h"
#include "TrackingTools/TransientTrack/interface/TransientTrackBuilder.h"

#include <algorithm>
#include <numeric>

//-----------------------------------------------------------------------------

std::vector<reco::PFCandidatePtr>
ff::getPFCands( const reco::PFJet& jet ) {
  std::vector<reco::PFCandidatePtr> result = jet.getPFConstituents();
  result.erase(
      std::remove_if( result.begin(), result.end(),
                      []( const auto& cand ) { return cand.isNull(); } ),
      result.end() );

  return result;
}

//-----------------------------------------------------------------------------

std::vector<reco::PFCandidatePtr>
ff::getChargedPFCands( const reco::PFJet& jet ) {
  std::vector<reco::PFCandidatePtr> result = getPFCands( jet );
  result.erase(
      std::remove_if( result.begin(), result.end(),
                      []( const auto& cand ) { return cand->charge() == 0; } ),
      result.end() );

  return result;
}

//-----------------------------------------------------------------------------

std::vector<reco::PFCandidatePtr>
ff::getTrackEmbededPFCands( const reco::PFJet& jet ) {
  std::vector<reco::PFCandidatePtr> result = getChargedPFCands( jet );
  result.erase( std::remove_if( result.begin(), result.end(),
                                []( const auto& cand ) {
                                  return cand->bestTrack() == nullptr;
                                } ),
                result.end() );

  return result;
}

//-----------------------------------------------------------------------------

std::vector<const reco::Track*>
ff::getSelectedTracks(
    const reco::PFJet&                          jet,
    const StringCutObjectSelector<reco::Track>& tkSelector ) {
  std::vector<const reco::Track*> result{};
  result.reserve( jet.chargedMultiplicity() );
  for ( const auto& cand : getTrackEmbededPFCands( jet ) ) {
    const reco::Track* tk = cand->bestTrack();
    if ( tkSelector( *tk ) ) {
      result.push_back( tk );
    }
  }

  return result;
}

//-----------------------------------------------------------------------------

float
ff::chargedMass( const reco::PFJet& jet ) {
  const auto cands = getChargedPFCands( jet );
  if ( cands.empty() )
    return 0.;

  auto result = ( *begin( cands ) )->p4();
  for ( auto canditer( next( begin( cands ) ) ); canditer != end( cands );
        ++canditer )
    result += ( *canditer )->p4();
  return result.M();
}

//-----------------------------------------------------------------------------

bool
ff::muonInTime( const reco::PFJet& jet, float timeLimit ) {
  // collect muon timing
  std::vector<float> muontimes{};
  for ( const auto& cand : getPFCands( jet ) ) {
    if ( cand->muonRef().isNonnull() and cand->muonRef()->isTimeValid() ) {
      muontimes.push_back( cand->muonRef()->time().timeAtIpInOut );
    }
  }

  // no muons in cands => muonInTime!
  if ( muontimes.empty() )
    return true;

  float muontimeMean =
      std::accumulate( muontimes.begin(), muontimes.end(), 0. ) /
      muontimes.size();
  bool result( true );

  // any time diff larger than limit => break loop
  for ( const auto& t : muontimes ) {
    if ( fabs( t - muontimeMean ) > timeLimit ) {
      result = false;
      break;
    }
  }

  return result;
}

//-----------------------------------------------------------------------------

int
ff::getNumberOfDisplacedStandAloneMuons(
    const reco::PFJet&                        jet,
    const edm::Handle<reco::TrackCollection>& generalTkH ) {
  std::vector<reco::PFCandidatePtr> candsWithTk = getTrackEmbededPFCands( jet );
  return std::count_if( candsWithTk.begin(), candsWithTk.end(),
                        [&generalTkH]( auto cand ) {
                          return cand->trackRef().isNonnull() and
                                 cand->trackRef().id() != generalTkH.id();
                        } );
}

//-----------------------------------------------------------------------------

float
ff::getTkIsolation( const reco::PFJet&                        jet,
                    const edm::Handle<reco::TrackCollection>& tkH,
                    const float&                              isoRadius ) {
  std::vector<reco::TrackRef> generalTkRefs{};
  for ( size_t i( 0 ); i != tkH->size(); ++i )
    generalTkRefs.emplace_back( tkH, i );

  std::vector<reco::PFCandidatePtr> cands = getTrackEmbededPFCands( jet );

  float notOfCands( 0. );
  for ( const auto& tkRef : generalTkRefs ) {
    if ( deltaR( jet, *tkRef ) > isoRadius )
      continue;  // outside radius

    if ( std::find_if( cands.begin(), cands.end(), [&tkRef]( const auto& c ) {
           return c->trackRef() == tkRef;
         } ) != cands.end() )
      continue;  // associated with the jet

    notOfCands += tkRef->pt();
  }

  float ofCands =
      std::accumulate( cands.begin(), cands.end(), 0.,
                       []( float ptsum, const reco::PFCandidatePtr& jc ) {
                         return ptsum + jc->bestTrack()->pt();
                       } );

  return ( ofCands + notOfCands ) == 0 ? NAN
                                       : notOfCands / ( ofCands + notOfCands );
}

//-----------------------------------------------------------------------------

float
ff::getPfIsolation( const reco::PFJet&                              jet,
                    const edm::Handle<reco::PFCandidateCollection>& pfH,
                    const float& isoRadius ) {
  std::vector<reco::PFCandidatePtr> pfCandPtrs{};
  for ( size_t i( 0 ); i != pfH->size(); ++i )
    pfCandPtrs.emplace_back( pfH, i );

  std::vector<reco::PFCandidatePtr> jetcands = getPFCands( jet );

  float notOfCands( 0. );
  for ( const auto& cand : pfCandPtrs ) {
    if ( deltaR( jet, *cand ) > isoRadius )
      continue;  // outside radius

    if ( std::find_if( jetcands.begin(), jetcands.end(),
                       [&cand]( const auto& jc ) { return jc == cand; } ) !=
         jetcands.end() )
      continue;  // associated with the jet

    notOfCands += cand->energy();
  }

  float ofCands =
      std::accumulate( jetcands.begin(), jetcands.end(), 0.,
                       []( float esum, const reco::PFCandidatePtr& jc ) {
                         return esum + jc->energy();
                       } );

  return ( ofCands + notOfCands ) == 0 ? NAN
                                       : notOfCands / ( ofCands + notOfCands );
}

//-----------------------------------------------------------------------------

float
ff::getNeutralIsolation( const reco::PFJet&                              jet,
                         const edm::Handle<reco::PFCandidateCollection>& pfH,
                         const float& isoRadius ) {
  std::vector<reco::PFCandidatePtr> pfCandPtrs{};
  for ( size_t i( 0 ); i != pfH->size(); ++i )
    pfCandPtrs.emplace_back( pfH, i );

  std::vector<reco::PFCandidatePtr> jetcands = getPFCands( jet );

  float notOfCands( 0. );
  for ( const auto& cand : pfCandPtrs ) {
    if ( cand->charge() != 0 )
      continue;  // charged
    if ( deltaR( jet, *cand ) > isoRadius )
      continue;  // outside radius

    if ( std::find_if( jetcands.begin(), jetcands.end(),
                       [&cand]( const auto& jc ) { return jc == cand; } ) !=
         jetcands.end() )
      continue;  // associated with the jet

    notOfCands += cand->energy();
  }

  float ofCands =
      std::accumulate( jetcands.begin(), jetcands.end(), 0.,
                       []( float esum, const reco::PFCandidatePtr& jc ) {
                         return esum + jc->energy();
                       } );

  return ( ofCands + notOfCands ) == 0 ? NAN
                                       : notOfCands / ( ofCands + notOfCands );
}

//-----------------------------------------------------------------------------

std::vector<reco::TransientTrack>
ff::transientTracksFromPFJet(
    const reco::PFJet&                          jet,
    const StringCutObjectSelector<reco::Track>& tkSelector,
    const edm::EventSetup&                      es ) {
  std::vector<reco::PFCandidatePtr> cands = getTrackEmbededPFCands( jet );

  edm::ESHandle<TransientTrackBuilder> theB;
  es.get<TransientTrackRecord>().get( "TransientTrackBuilder", theB );

  std::vector<reco::TransientTrack> t_tks{};
  for ( const auto& c : cands ) {
    if ( !tkSelector( *( c->bestTrack() ) ) )
      continue;
    reco::TransientTrack tt = theB->build( c );
    if ( !tt.isValid() )
      continue;
    t_tks.push_back( tt );
  }

  return t_tks;
}

//-----------------------------------------------------------------------------
