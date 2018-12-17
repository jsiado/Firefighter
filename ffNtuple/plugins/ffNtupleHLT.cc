#include "Firefighter/ffNtuple/interface/ffNtupleBase.h"

#include "DataFormats/Math/interface/LorentzVectorFwd.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/HLTReco/interface/TriggerObject.h"
#include "DataFormats/HLTReco/interface/TriggerEvent.h"

#include <map>

class ffNtupleHLT : public ffNtupleBase
{
  public:
    ffNtupleHLT(const edm::ParameterSet&);
    ~ffNtupleHLT();

    void initialize(TTree&, const edm::ParameterSet&, edm::ConsumesCollector&&) final;
    void fill(const edm::Event&, const edm::EventSetup&) override {}
    void fill(const edm::Event&, const edm::EventSetup&, HLTConfigProvider&) final;

  private:
    void clear() final;

    edm::EDGetToken hlt_eventToken_;
    edm::EDGetToken hlt_resultToken_;

    

    std::vector<std::string> hlt_pathsNoVer_;
    std::map<std::string, bool> hlt_bit_;
    std::map<std::string, math::XYZTLorentzVectorFCollection> hlt_triggerObjectP4_;
};

DEFINE_EDM_PLUGIN(ffNtupleFactory,
                  ffNtupleHLT,
                  "ffNtupleHLT");

ffNtupleHLT::ffNtupleHLT(const edm::ParameterSet& ps) :
  ffNtupleBase(ps)
{}

ffNtupleHLT::~ffNtupleHLT()
{
  hlt_pathsNoVer_.clear();
  hlt_bit_.clear();
  hlt_triggerObjectP4_.clear();
}

void
ffNtupleHLT::initialize(TTree& tree,
                        const edm::ParameterSet& ps,
                        edm::ConsumesCollector&& cc)
{
  hlt_eventToken_ = cc.consumes<trigger::TriggerEvent>(ps.getParameter<edm::InputTag>("TriggerEvent"));
  hlt_resultToken_ = cc.consumes<edm::TriggerResults>(ps.getParameter<edm::InputTag>("TriggerResults"));
  hlt_pathsNoVer_ = ps.getParameter<std::vector<std::string>>("TriggerPaths");
  
  for (const auto& p : hlt_pathsNoVer_)
  {
    hlt_bit_[p] = false;
    hlt_triggerObjectP4_[p] = math::XYZTLorentzVectorFCollection();

    tree.Branch(p.c_str(), &hlt_bit_[p], (p+"/O").c_str());
    tree.Branch(("TO"+p).c_str(), &hlt_triggerObjectP4_[p]);
  }
}

void
ffNtupleHLT::fill(const edm::Event& e,
                  const edm::EventSetup& es,
                  HLTConfigProvider& hcp)
{
  using namespace std;

  edm::Handle<trigger::TriggerEvent> hlt_eventH;
  e.getByToken(hlt_eventToken_, hlt_eventH);
  
  edm::Handle<edm::TriggerResults> hlt_resultH;
  e.getByToken(hlt_resultToken_, hlt_resultH);

  assert(hlt_eventH.isValid() && hlt_resultH.isValid());
  clear();

  const vector<string>& allTriggerPaths = hcp.triggerNames();
  
  for (const auto& p : hlt_pathsNoVer_)
  {

    const vector<string> matchedPaths(hcp.restoreVersion(allTriggerPaths, p));
    if (matchedPaths.size() == 0) {
      throw cms::Exception("Could not find matched full trigger path with -> "+p);
    }
    const std::string trigPath  = matchedPaths[0];
    const auto triggerPathIndex = hcp.triggerIndex(trigPath);
    if (triggerPathIndex >= hcp.size()) {
      throw cms::Exception("Cannot find trigger path -> "+trigPath);
    }
    
    if (!hlt_resultH->wasrun(triggerPathIndex) or hlt_resultH->error(triggerPathIndex)) continue;
    
    hlt_bit_[p] = hlt_resultH->accept(triggerPathIndex);

    if (!hlt_resultH->accept(triggerPathIndex)) continue;

    // picking out last filter(index) of this trigger p.
    trigger::size_type lastFilterIndex(hlt_eventH->sizeFilters());
    const vector<string>& nameModules = hcp.moduleLabels(triggerPathIndex);
    size_t iM = nameModules.size();
    while (iM>0)
    {
      const string& nameFilter = nameModules[--iM];
      if (hcp.moduleEDMType(nameFilter) != "EDFilter") continue;
      if (!hcp.saveTags(nameFilter)) continue;
      
      lastFilterIndex = hlt_eventH->filterIndex(edm::InputTag(nameFilter, "", "HLT"));
      break;
    }

    if (lastFilterIndex >= hlt_eventH->sizeFilters()) continue;

    // filling trigger objects' indexes.
    set<trigger::size_type> triggerObjectIndices{};
    
    const trigger::Keys& keys = hlt_eventH->filterKeys(lastFilterIndex);
    const trigger::Vids& types= hlt_eventH->filterIds(lastFilterIndex);

    for (size_t iK(0); iK!=keys.size(); ++iK) {
      if (types[iK]!=trigger::TriggerObjectType::TriggerL1Mu and
          types[iK]!=trigger::TriggerObjectType::TriggerMuon) { continue; }
      triggerObjectIndices.emplace(keys[iK]);
    }

    for (const auto& iTOidx: triggerObjectIndices)
    {
      const auto& iTO = (hlt_eventH->getObjects())[iTOidx];
      hlt_triggerObjectP4_[p].emplace_back(iTO.px(), iTO.py(), iTO.pz(), iTO.energy());
    }

  }

}

void
ffNtupleHLT::clear()
{
  for (const auto& p : hlt_pathsNoVer_)
  {
    hlt_bit_[p] = false;
    hlt_triggerObjectP4_[p].clear();
  }
}