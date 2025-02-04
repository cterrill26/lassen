from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def utaa_s1_pipelined_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class utaa_s1_pipelined(Peak):
        def __call__(self, in2: Data, in1: Data, in0: Data) -> Data:

            return Data(UInt(in1) + (UInt(in2) + UInt(in0)))

    return utaa_s1_pipelined
