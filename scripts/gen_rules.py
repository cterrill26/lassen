from lassen.sim import gen_pe
import lassen.asm as asm
from hwtypes import BitVector
import coreir
import metamapper as mm
import pytest
import json

def discover(file_name):

    c = coreir.Context()
    mapper = mm.PeakMapper(c,"pe_ns")
    mapper.add_peak_primitive("PE",gen_pe)

    def bypass_mode(inst):
        return (
            inst.rega == type(inst.rega).BYPASS and
            inst.regb == type(inst.regb).BYPASS and
            inst.regd == type(inst.regd).BYPASS and
            inst.rege == type(inst.rege).BYPASS and
            inst.regf == type(inst.regf).BYPASS
        )
    mapper.add_discover_constraint(bypass_mode)
    rrs = mapper.discover_peak_rewrite_rules(width=16,coreir_primitives=["add","sub","or"],serialize=True,verbose=True)
    print(rrs)

    with open(file_name,'w') as jfile:
        json.dump(rrs,jfile,indent=2)

discover('rules/simple.json')
