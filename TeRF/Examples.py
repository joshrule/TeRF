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
small_numbers = [Op.Op(str(n), 0) for n in xrange(10)]
numbers = [Op.Op(str(n), 0) for n in xrange(100)]


CONS2 = Op.Op('cons', 2)
HEAD1 = Op.Op('head', 1)
TAIL1 = Op.Op('tail', 1)
CONST1 = Op.Op('const', 1)
COUNT2 = Op.Op('count', 2)
SUCC1 = Op.Op('s', 1)
LENGTH1 = Op.Op('length', 1)


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
syntax = {
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
    TAIL: TBind.TBind(vJ, ty.function(List(vJ), List(vJ)))}

# head_syntax = {
#     NIL: TBind.TBind(vC, List(vC)),
#     CONS: TBind.TBind(vD,
#                       ty.function(vD,
#                                   ty.function(List(vD),
#                                               List(vD)))),
#     DOT: TBind.TBind(vA, TBind.TBind(vB,
#                                      ty.function(ty.function(vA, vB),
#                                                  ty.function(vA, vB)))),
#     HEAD: TBind.TBind(vE, ty.function(List(vE), vE))}
#
# head_syntax_with_numbers = copy.copy(head_syntax)
# head_syntax_with_numbers.update({n: NAT for n in numbers})
#
# simple_syntax = {
#     NIL: List(NAT),
#     CONS: ty.function(NAT, ty.function(List(NAT), List(NAT))),
#     DOT: TBind.TBind(vA, TBind.TBind(vB,
#                                      ty.function(ty.function(vA, vB),
#                                                  ty.function(vA, vB)))),
#     HEAD: ty.function(List(NAT), NAT)}
# simple_syntax.update({n: NAT for n in small_numbers})

head1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    HEAD1: ty.function(List(NAT), NAT)}
head1_syntax.update({n: NAT for n in small_numbers})

tail1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    TAIL1: ty.function(List(NAT), List(NAT))}
tail1_syntax.update({n: NAT for n in small_numbers})

headtail_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    HEAD1: ty.function(List(NAT), NAT),
    TAIL1: ty.function(List(NAT), List(NAT))}
headtail_syntax.update({n: NAT for n in small_numbers})

const1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    CONST1: ty.function(List(NAT), NAT)}
const1_syntax.update({n: NAT for n in small_numbers})

count1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    COUNT2: ty.function(NAT, ty.function(List(NAT), NAT)),
    SUCC1: ty.function(NAT, NAT)}
count1_syntax.update({n: NAT for n in small_numbers})

length1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    LENGTH1: ty.function(List(NAT), NAT),
    ZERO: NAT,
    SUCC1: ty.function(NAT, NAT)}
# length1_syntax.update({n: NAT for n in small_numbers})


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
head0_template = Rule.Rule(j(HEAD, hole()),
                           hole(), True)

tail0_template = Rule.Rule(j(TAIL, hole()),
                           hole(), True)

head1_templates = [Rule.Rule(App.App(HEAD1, [hole()]),
                             hole(), True),
                   Rule.Rule(App.App(HEAD1, [f(NIL)]),
                             hole(), True),
                   Rule.Rule(App.App(HEAD1, [App.App(CONS2,
                                                     [hole(), hole()])]),
                             hole(), True)]

tail1_templates = [Rule.Rule(App.App(TAIL1, [hole()]),
                             hole(), True),
                   Rule.Rule(App.App(TAIL1, [f(NIL)]),
                             hole(), True),
                   Rule.Rule(App.App(TAIL1, [App.App(CONS2,
                                                     [hole(), hole()])]),
                             hole(), True)]

const1_templates = [Rule.Rule(App.App(CONST1, [hole()]),
                              hole(), True),
                    Rule.Rule(App.App(CONST1, [f(NIL)]),
                              hole(), True),
                    Rule.Rule(App.App(CONST1, [App.App(CONS2,
                                                       [hole(), hole()])]),
                              hole(), True)]

count2_template = Rule.Rule(App.App(COUNT2, [hole(), hole()]),
                            hole(), True)

length1_templates = [Rule.Rule(App.App(LENGTH1, [hole()]),
                               hole(), True),
                     Rule.Rule(App.App(LENGTH1, [f(NIL)]),
                               hole(), True),
                     Rule.Rule(App.App(LENGTH1, [App.App(CONS2,
                                                         [hole(), hole()])]),
                               hole(), True)]

# headtail_templates = [head1_template, tail1_template]