from peak import Peak, family_closure, Const
from peak import family
from peak.family import AbstractFamily


@family_closure
def bit_or_pipelined_fc(family: AbstractFamily):
    Data = family.BitVector[16]
    Data32 = family.Unsigned[32]
    SInt = family.Signed[16]
    UInt = family.Unsigned[16]
    Bit = family.Bit

    @family.assemble(locals(), globals())
    class bit_or_pipelined(Peak):
        def __call__(self, in1: Bit, in0: Bit) -> Bit:

            return Bit(Bit(in0) | Bit(in1))

    return bit_or_pipelined
