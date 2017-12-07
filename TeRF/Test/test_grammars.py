import TeRF.Types.Application as A
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as R
import TeRF.Types.TRS as TRS
import TeRF.Types.TypeSystem as TS
import TeRF.Types.Variable as V


def f(x, xs=None):
    if xs is None:
        xs = []
    return A.App(x, xs)


def g(x, y):
    return A.App(DOT, [x, y])


def h(x, y):
    return A.App(DOT, [f(x), f(y)])


def j(x, y):
    return A.App(DOT, [f(x), y])


def k(x, y):
    return A.App(DOT, [x, f(y)])


# Declare some Primitives #####################################################
NIL = Op.Operator('nil', 0)
CONS = Op.Operator('cons', 0)
ZERO = Op.Operator('0', 0)
ONE = Op.Operator('1', 0)
TWO = Op.Operator('2', 0)
THREE = Op.Operator('3', 0)
DOT = Op.Operator('.', 2)
HEAD = Op.Operator('head', 0)
numbers = [Op.Operator(str(i), 0) for i in xrange(100)]

# Setup 2 TypeSystems #########################################################
NAT = TS.TypeOperator('NAT', [])
vA = TS.TypeVariable()
vB = TS.TypeVariable()
vC = TS.TypeVariable()
vD = TS.TypeVariable()
vE = TS.TypeVariable()
vF = TS.TypeVariable()
vG = TS.TypeVariable()
vH = TS.TypeVariable()


class List(TS.TypeOperator):
    def __init__(self, alpha_type):
        super(List, self).__init__('LIST', [alpha_type])


class Pair(TS.TypeOperator):
    def __init__(self, alpha_type, beta_type):
        super(Pair, self).__init__('PAIR', [alpha_type, beta_type])


syntax = TS.TypeSystem(
    {NIL: TS.TypeBinding(vC, List(vC)),
     ZERO: NAT,
     ONE: NAT,
     TWO: NAT,
     THREE: NAT,
     CONS: TS.TypeBinding(vD,
                          TS.Function(vD,
                                      TS.Function(List(vD),
                                                  List(vD)))),
     DOT: TS.TypeBinding(vA, TS.TypeBinding(vB,
                                            TS.Function(TS.Function(vA, vB),
                                                        TS.Function(vA, vB)))),
     HEAD: TS.TypeBinding(vE, TS.Function(List(vE), vE))})

simple_syntax = TS.TypeSystem(
    {NIL: List(NAT),
     ZERO: NAT,
     ONE: NAT,
     TWO: NAT,
     THREE: NAT,
     CONS: TS.Function(NAT,
                       TS.Function(List(NAT),
                                   List(NAT))),
     DOT: TS.TypeBinding(vA, TS.TypeBinding(vB,
                                            TS.Function(TS.Function(vA, vB),
                                                        TS.Function(vA, vB)))),
     HEAD: TS.Function(List(NAT), NAT)})

# Setup a TRS #################################################################

X = V.Var('x')
Y = V.Var('y')
Z = V.Var('z')

head_lhs = g(f(HEAD), g(g(f(CONS), X), Y))
head_rhs = X
head_rule = R.Rule(head_lhs, head_rhs)

semantics = TRS.TRS(rules={head_rule}, rule_type=NAT)

# head_lot = LOT.LOT(primitives=head_fpcfg, syntax=head_pcfg, semantics=head_g)
#
# # make some test data
# head_datum_T = R.Rule(g(f(HEAD),
#                         g(g(f(CONS), f(ZERO)),
#                           g(g(f(CONS), f(ONE)),
#                             g(g(f(CONS), f(TWO)),
#                               g(g(f(CONS), f(THREE)),
#                                 f(NIL)))))),
#                       f(ZERO))
#
# head_datum_T2 = R.Rule(g(f(HEAD),
#                          g(g(f(CONS), f(ONE)),
#                            g(g(f(CONS), f(THREE)),
#                              g(g(f(CONS), f(TWO)),
#                                f(NIL))))),
#                        f(ONE))
#
# head_datum_T3 = R.Rule(g(f(HEAD),
#                          g(g(f(CONS), f(TWO)),
#                            f(NIL))),
#                        f(TWO))
#
# head_datum_F = R.Rule(g(f(HEAD),
#                         g(g(f(CONS), f(ZERO)),
#                           g(g(f(CONS), f(ONE)),
#                             g(g(f(CONS), f(TWO)),
#                               g(g(f(CONS), f(THREE)),
#                                 f(NIL)))))),
#                       f(NIL))
#
# list_datum_T = R.Rule(f(LIST),
#                       g(g(f(CONS), f(ZERO)),
#                         g(g(f(CONS), f(ONE)),
#                           g(g(f(CONS), f(TWO)),
#                             f(NIL)))))
#
# list_datum_F = R.Rule(f(LIST),
#                       g(g(f(ONE), f(ZERO)),
#                         f(NIL)))
#
# # full head syntax
# rule_START = R.Rule(f(START), {f(LIST), f(NUMBER)})
# rule_LIST = R.Rule(f(LIST), {f(NIL), f(NEL)})
# rule_NEL = R.Rule(f(NEL), g(g(f(CONS), f(NUMBER)), f(LIST)))
# rule_NUMBER = R.Rule(f(NUMBER), {f(N) for N in NUMBERS})
# rule_HEAD = R.Rule(f(NUMBER), g(f(HEAD), f(NEL)))
#
# full_head_pcfg = CFG.PCFG(rules={rule_START, rule_LIST, rule_NEL,
#                                  rule_NUMBER, rule_HEAD},
#                           start=f(START), locked=False)
