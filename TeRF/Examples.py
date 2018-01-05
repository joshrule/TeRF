import copy
import TeRF.Miscellaneous as misc
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Types.Application as App
import TeRF.Types.Hole as Hole
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as Rule
import TeRF.Types.TypeBinding as TBind
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.Variable as Var
import TeRF.Types.TRS as TRS
import TeRF.Types.LOT as LOT


# Utility Functions ###########################################################
def f(x, xs=None):
    if xs is None:
        xs = []
    return App.App(x, xs)


def g(x, y):
    return App.App(DOT, [x, y])


def h(x, y):
    return App.App(DOT, [f(x), f(y)])


def j(x, y):
    return App.App(DOT, [f(x), y])


def k(x, y):
    return App.App(DOT, [x, f(y)])


def hole():
    return Hole.Hole()


# Operators ###################################################################
NIL = Op.Op('nil', 0)
CONS = Op.Op('cons', 0)
ZERO = Op.Op('0', 0)
ONE = Op.Op('1', 0)
TWO = Op.Op('2', 0)
THREE = Op.Op('3', 0)
DOT = Op.Op('.', 2)
HEAD = Op.Op('head', 0)
TAIL = Op.Op('tail', 0)
ID = Op.Op('id', 0)
numbers = [Op.Op(str(n), 0) for n in xrange(100)]


# Variables ###################################################################
X = Var.Var('x')
Y = Var.Var('y')
Z = Var.Var('z')


# TypeOperators ###############################################################
NAT = TOp.TOp('NAT', [])


class List(TOp.TOp):
    def __init__(self, alpha_type):
        super(List, self).__init__('LIST', [alpha_type])


# TypeVariables ###############################################################
vA = TVar.TVar()
vB = TVar.TVar()
vC = TVar.TVar()
vD = TVar.TVar()
vE = TVar.TVar()
vF = TVar.TVar()
vG = TVar.TVar()
vH = TVar.TVar()
vI = TVar.TVar()
vJ = TVar.TVar()


# TypeSystem ##################################################################
syntax = misc.edict({
    NIL: TBind.TBind(vC, List(vC)),
    ZERO: NAT,
    ONE: NAT,
    TWO: NAT,
    THREE: NAT,
    CONS: TBind.TBind(vD,
                      ty.function(vD,
                                  ty.function(List(vD),
                                              List(vD)))),
    DOT: TBind.TBind(vA, TBind.TBind(vB,
                                     ty.function(ty.function(vA, vB),
                                                 ty.function(vA, vB)))),
    ID: TBind.TBind(vC, ty.function(vC, vC)),
    HEAD: TBind.TBind(vE, ty.function(List(vE), vE)),
    TAIL: TBind.TBind(vJ, ty.function(List(vJ), List(vJ)))})
syntax.fvs = ty.free_vars_in_env(syntax)

head_syntax = misc.edict({
    NIL: TBind.TBind(vC, List(vC)),
    CONS: TBind.TBind(vD,
                      ty.function(vD,
                                  ty.function(List(vD),
                                              List(vD)))),
    DOT: TBind.TBind(vA, TBind.TBind(vB,
                                     ty.function(ty.function(vA, vB),
                                                 ty.function(vA, vB)))),
    HEAD: TBind.TBind(vE, ty.function(List(vE), vE))})
head_syntax.fvs = ty.free_vars_in_env(head_syntax)

head_syntax_with_numbers = copy.copy(head_syntax)
head_syntax_with_numbers.update({n: NAT for n in numbers})
head_syntax_with_numbers.fvs = ty.free_vars_in_env(head_syntax_with_numbers)


# TRS #########################################################################


head_lhs_1 = j(HEAD, g(j(CONS, X), Y))
head_rhs_1 = X
head_rule_1 = Rule.Rule(head_lhs_1, head_rhs_1)

tail_lhs_1 = j(TAIL, g(j(CONS, X), Y))
tail_rhs_1 = Y
tail_rule_1 = Rule.Rule(tail_lhs_1, tail_rhs_1)

tail_lhs_2 = h(TAIL, NIL)
tail_rhs_2 = f(NIL)
tail_rule_2 = Rule.Rule(tail_lhs_2, tail_rhs_2)

semantics = TRS.TRS(rules={head_rule_1, tail_rule_1, tail_rule_2})


# LOT #########################################################################
head_lot = LOT.LOT(syntax, semantics)


# Rules #######################################################################
head_datum_T = Rule.Rule(g(f(HEAD),
                           g(g(f(CONS), f(ZERO)),
                             g(g(f(CONS), f(ONE)),
                               g(g(f(CONS), f(TWO)),
                                 g(g(f(CONS), f(THREE)),
                                   f(NIL)))))),
                         f(ZERO))

head_datum_T2 = Rule.Rule(g(f(HEAD),
                            g(g(f(CONS), f(ONE)),
                              g(g(f(CONS), f(THREE)),
                                g(g(f(CONS), f(TWO)),
                                  f(NIL))))),
                          f(ONE))

head_datum_T3 = Rule.Rule(g(f(HEAD),
                            g(g(f(CONS), f(TWO)),
                              f(NIL))),
                          f(TWO))

head_datum_F = Rule.Rule(g(f(HEAD),
                           g(g(f(CONS), f(ZERO)),
                             g(g(f(CONS), f(ONE)),
                               g(g(f(CONS), f(TWO)),
                                 g(g(f(CONS), f(THREE)),
                                   f(NIL)))))),
                         f(NIL))


# Templates ###################################################################
head_template = Rule.Rule(j(HEAD, hole()),
                          hole(), True)

tail_template = Rule.Rule(j(TAIL, hole()),
                          hole(), True)
