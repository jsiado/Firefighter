#!/usr/bin/env python

# controls all switches

switches = {
    "jobtype": "data_abc",  # {'data_abc', 'data_d', 'sigmc', 'bkgmc'}
    "region": "control",  # {'all', 'signal', 'control', 'single'}
    "recoStuff": {"leptonCandOnly": True, "usingCHS": False},
}


assert switches["jobtype"] in ["data_abc", "data_d", "sigmc", "bkgmc"]
assert switches["region"] in ["all", "signal", "control", "single"]
assert (
    switches["recoStuff"]["leptonCandOnly"]
    and switches["recoStuff"]["usingCHS"] is False
)