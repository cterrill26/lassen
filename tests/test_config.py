import os
from collections import namedtuple
import lassen.asm as asm
from lassen.sim import gen_pe, gen_pe_type_family
from lassen.mode import gen_mode_type
from lassen.isa import *
from hwtypes import SIntVector, UIntVector, BitVector, Bit, FPVector, RoundingMode
import pytest
import magma
import peak
import fault
from itertools import product
import os
import random
import shutil
from peak.assembler import Assembler
import random

class HashableDict(dict):
    def __hash__(self):
        return hash(tuple(sorted(self.keys())))

Bit = Bit
Data = BitVector[DATAWIDTH]
Data32 = BitVector[32]
Data8 = BitVector[32]
BFloat16 = FPVector[8,7,RoundingMode.RNE,False]

pe_ = gen_pe(BitVector.get_family())
pe = pe_()
sim_family = gen_pe_type_family(BitVector.get_family())
Mode = gen_mode_type(sim_family)

# create these variables in global space so that we can reuse them easily
instr_name, inst_type = pe.__call__._peak_isa_
_assembler = Assembler(inst_type)
assembler = _assembler.assemble
disassembler = _assembler.disassemble
width = _assembler.width
layout = _assembler.layout
NTESTS = 16

def write_data01(pe,data0 : Data, data1 : Data,instr=asm.add(),ra=Data(0)):
    config_addr = Data8(DATA01_ADDR)
    config_data = BitVector.concat(data0,data1)
    config_en = Bit(1)
    return pe(instr,data0=ra,config_addr=config_addr,config_data=config_data,config_en=config_en)

def read_data0(pe,instr=asm.add(),ra=Data(0)):
    config_addr = Data8(DATA01_ADDR)
    _,_,config_read = pe(instr,data0=ra,config_addr=config_addr)
    return config_read[DATA0_START:DATA0_START+DATA0_WIDTH]

def read_data1(pe):
    instr = asm.add()
    config_addr = Data8(DATA01_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[DATA1_START:DATA1_START+DATA1_WIDTH]

@pytest.mark.parametrize("args",[
    (BitVector.random(DATAWIDTH), BitVector.random(DATAWIDTH))
        for _ in range(NTESTS)
])
def test_config_data01(args):
    write_data01(pe,args[0],args[1])
    assert args[0] == read_data0(pe)
    assert args[1] == read_data1(pe)

def write_bit012(pe,bit0 : Bit, bit1 : Bit, bit2 : Bit, instr=asm.add()):
    BV1 = BitVector[1]
    config_addr = Data8(BIT012_ADDR)
    config_data = BitVector.concat(BitVector.concat(BitVector.concat(BV1(bit0),BV1(bit1)),BV1(bit2)),BitVector[29](0))
    config_en = Bit(1)
    return pe(instr,data0=Data(0),config_addr=config_addr,config_data=config_data,config_en=config_en)

def read_bit0(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT0_START]

def read_bit1(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT1_START]

def read_bit2(pe):
    instr = asm.add()
    config_addr = Data8(BIT012_ADDR)
    _,_,config_read = pe(instr,Data(0),config_addr=config_addr)
    return config_read[BIT2_START]

@pytest.mark.parametrize("args",[
    (Bit(random.randint(0,1)),
     Bit(random.randint(0,1)),
     Bit(random.randint(0,1)))
        for _ in range(NTESTS)
])
def test_config_bit012(args):
    write_bit012(pe,args[0],args[1],args[2])
    assert args[0] == read_bit0(pe)
    assert args[1] == read_bit1(pe)
    assert args[2] == read_bit2(pe)


#Properties that must hold, config_en has higher priority over the input
@pytest.mark.parametrize("args",[
    (BitVector.random(DATAWIDTH),
     BitVector.random(DATAWIDTH),
     BitVector.random(DATAWIDTH))
        for _ in range(NTESTS)
])
def test_write_priority_data0(args):
    instr = asm.add(ra_mode=Mode.DELAY)
    write_data01(pe,data0=args[0],data1=args[1],instr=instr,ra=args[2])
    #The config takes prioirty over the ra input
    assert args[0] == read_data0(pe,instr=instr,ra=args[2])
    #Now data0 register should contain args[2] (from delay)
    assert args[2] == read_data0(pe,instr=instr,ra=args[1])
    assert args[1] == read_data0(pe,instr=instr)
    #data1 should still contain args[1] from the first write_data01
    assert args[1] == read_data1(pe)


