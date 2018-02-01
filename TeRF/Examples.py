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
very_small_numbers = [Op.Op(str(n), 0) for n in xrange(3)]
small_numbers = [Op.Op(str(n), 0) for n in xrange(10)]
numbers = [Op.Op(str(n), 0) for n in xrange(100)]


ADD2 = Op.Op('add', 2)
CAT2 = Op.Op('cat', 2)
CHASOT1 = Op.Op('compare_head_and_sum_of_tail', 1)
CHIT1 = Op.Op('chit', 1)
CONS2 = Op.Op('cons', 2)
CONST1 = Op.Op('const', 1)
COUNT2 = Op.Op('count', 2)
COUNT31 = Op.Op('count3', 1)
CUMSUM1 = Op.Op('cumsum', 1)
DEDUPLICATE1 = Op.Op('deduplicate', 1)
EVEN1 = Op.Op('even', 1)
FILTER_EVEN1 = Op.Op('filter_even', 1)
GREATER2 = Op.Op('greater', 2)
HEAD1 = Op.Op('head', 1)
IF3 = Op.Op('if', 3)
IIH1 = Op.Op('index_in_head', 1)
INCREMENT1 = Op.Op('increment', 1)
INSERT2 = Op.Op('insert', 2)
LAST1 = Op.Op('last', 1)
LENGTH1 = Op.Op('length', 1)
NTH2 = Op.Op('nth', 2)
REMOVE2 = Op.Op('remove', 2)
SORT1 = Op.Op('sort', 1)
SUCC1 = Op.Op('s', 1)
SUM1 = Op.Op('sum', 1)
SUMPRIM1 = Op.Op('sum_prim', 1)
TAIL1 = Op.Op('tail', 1)
UNTIL2 = Op.Op('until', 2)

P11 = Op.Op('p11', 1)
P12 = Op.Op('p12', 1)
P13 = Op.Op('p13', 1)
P21 = Op.Op('p21', 2)
P22 = Op.Op('p22', 2)
P23 = Op.Op('p23', 2)

# Variables ###################################################################
X = Var.Var('x')
Y = Var.Var('y')
Z = Var.Var('z')

# TypeOperators ###############################################################
NAT = TOp.TOp('NAT', [])
BOOL = TOp.TOp('BOOL', [])


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

bg_syntax = {
    NIL: List(NAT),
    COUNT2: ty.function(NAT, ty.function(List(NAT), NAT)),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    SUCC1: ty.function(NAT, NAT),
    ZERO: NAT,
    SUMPRIM1: ty.function(List(NAT), NAT),
    ADD2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    INSERT2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    REMOVE2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    EVEN1: ty.function(NAT, BOOL),
    GREATER2: ty.function(NAT, ty.function(NAT, BOOL)),
    IF3: ty.function(BOOL, ty.function(List(NAT), ty.function(List(NAT),
                                                              List(NAT)))),
    NTH2: ty.function(NAT, ty.function(List(NAT), NAT))
    }
bg_syntax.update({n: NAT for n in very_small_numbers})

e1_const1_syntax = bg_syntax.copy()
e1_const1_syntax.update({CONST1: ty.function(List(NAT), NAT)})

e1_head1_syntax = bg_syntax.copy()
e1_head1_syntax.update({HEAD1: ty.function(List(NAT), NAT)})

e1_sum1_syntax = bg_syntax.copy()
e1_sum1_syntax.update({SUM1: ty.function(List(NAT), NAT)})

e1_increment1_syntax = bg_syntax.copy()
e1_increment1_syntax.update({INCREMENT1: ty.function(List(NAT), List(NAT))})

e1_sort1_syntax = bg_syntax.copy()
e1_sort1_syntax.update({SORT1: ty.function(List(NAT), List(NAT))})

e1_length1_syntax = bg_syntax.copy()
e1_length1_syntax.update({LENGTH1: ty.function(List(NAT), NAT)})

e1_deduplicate1_syntax = bg_syntax.copy()
e1_deduplicate1_syntax.update(
    {DEDUPLICATE1: ty.function(List(NAT), List(NAT))})

e1_cumsum1_syntax = bg_syntax.copy()
e1_cumsum1_syntax.update({CUMSUM1: ty.function(List(NAT), List(NAT))})

e1_filter_even1_syntax = bg_syntax.copy()
e1_filter_even1_syntax.update(
    {FILTER_EVEN1: ty.function(List(NAT), List(NAT))})

e1_index_in_head1_syntax = bg_syntax.copy()
e1_index_in_head1_syntax.update({IIH1: ty.function(List(NAT), NAT)})

e1_compare_head_and_sum_of_tail1_syntax = bg_syntax.copy()
e1_compare_head_and_sum_of_tail1_syntax.update(
    {CHASOT1: ty.function(List(NAT), NAT)})

e1_count31_syntax = bg_syntax.copy()
e1_count31_syntax.update({COUNT31: ty.function(List(NAT), NAT)})

e2_head1_syntax = bg_syntax.copy()
e2_head1_syntax.update({HEAD1: ty.function(List(NAT), NAT)})

e2_tail1_syntax = bg_syntax.copy()
e2_tail1_syntax.update({TAIL1: ty.function(List(NAT), List(NAT))})

e2_count31_syntax = bg_syntax.copy()
e2_count31_syntax.update({COUNT31: ty.function(List(NAT), NAT)})

e2_good_chit1_syntax = bg_syntax.copy()
e2_good_chit1_syntax.update({
    CHIT1: ty.function(List(NAT), NAT),
    COUNT31: ty.function(List(NAT), NAT),
    HEAD1: ty.function(List(NAT), NAT),
    TAIL1: ty.function(List(NAT), List(NAT)),
    P11: ty.function(vA, vB),
    P12: ty.function(vC, vD),
    P21: ty.function(vE, ty.function(vF, vG))})

e2_bad_chit1_syntax = bg_syntax.copy()
e2_bad_chit1_syntax.update({
    CHIT1: ty.function(List(NAT), NAT),
    UNTIL2: ty.function(NAT, ty.function(List(NAT), NAT)),
    LENGTH1: ty.function(List(NAT), NAT),
    LAST1: ty.function(List(NAT), NAT),
    P11: ty.function(vA, vB),
    P12: ty.function(vC, vD),
    P21: ty.function(vE, ty.function(vF, vG))})

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

count2_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    COUNT2: ty.function(NAT, ty.function(List(NAT), NAT)),
    SUCC1: ty.function(NAT, NAT)}
count2_syntax.update({n: NAT for n in small_numbers})

count31_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    COUNT2: ty.function(NAT, ty.function(List(NAT), NAT)),
    COUNT31: ty.function(List(NAT), NAT),
    SUCC1: ty.function(NAT, NAT)}
count31_syntax.update({n: NAT for n in small_numbers})

length1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    LENGTH1: ty.function(List(NAT), NAT),
    ZERO: NAT,
    SUCC1: ty.function(NAT, NAT)}
# length1_syntax.update({n: NAT for n in small_numbers})

last1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    LAST1: ty.function(List(NAT), NAT),
    ZERO: NAT,
    SUCC1: ty.function(NAT, NAT)}
# length1_syntax.update({n: NAT for n in small_numbers})

cat2_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    CAT2: ty.function(List(NAT), ty.function(List(NAT), NAT)),
    ZERO: NAT,
    SUCC1: ty.function(NAT, NAT)}

chit1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    CHIT1: ty.function(List(NAT), NAT),
    SUCC1: ty.function(NAT, NAT),
    COUNT2: ty.function(NAT, ty.function(List(NAT), NAT)),
    HEAD1: ty.function(List(NAT), NAT),
    TAIL1: ty.function(List(NAT), List(NAT)),
    P11: ty.function(vA, vB),
    P12: ty.function(vC, vD),
    P21: ty.function(vE, ty.function(vF, vG))
}
chit1_syntax.update({n: NAT for n in small_numbers})

bad_chit1_syntax = {
    NIL: List(NAT),
    CONS2: ty.function(NAT, ty.function(List(NAT), List(NAT))),
    CHIT1: ty.function(List(NAT), NAT),
    SUCC1: ty.function(NAT, NAT),
    UNTIL2: ty.function(NAT, ty.function(List(NAT), NAT)),
    LENGTH1: ty.function(List(NAT), NAT),
    LAST1: ty.function(List(NAT), NAT),
    P11: ty.function(vA, vB),
    P12: ty.function(vC, vD),
    P21: ty.function(vE, ty.function(vF, vG))}
bad_chit1_syntax.update({n: NAT for n in small_numbers})

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

length1_templates = [Rule.Rule(App.App(LENGTH1, [hole()]),
                               hole(), True),
                     Rule.Rule(App.App(LENGTH1, [f(NIL)]),
                               hole(), True),
                     Rule.Rule(App.App(LENGTH1, [App.App(CONS2,
                                                         [hole(), hole()])]),
                               hole(), True)]

last1_templates = [Rule.Rule(App.App(LAST1, [hole()]),
                             hole(), True),
                   Rule.Rule(App.App(LAST1, [f(NIL)]),
                             hole(), True),
                   Rule.Rule(App.App(LAST1, [App.App(CONS2,
                                                       [hole(), hole()])]),
                             hole(), True)]


chit1_templates = [Rule.Rule(App.App(CHIT1, [hole()]),
                             hole(), True),
                   Rule.Rule(App.App(CHIT1, [f(NIL)]),
                             hole(), True),
                   Rule.Rule(App.App(CHIT1, [App.App(CONS2,
                                                     [hole(), hole()])]),
                             hole(), True)]

bad_chit1_templates = [Rule.Rule(App.App(CHIT1, [hole()]),
                                 hole(), True),
                       Rule.Rule(App.App(CHIT1, [f(NIL)]),
                                 hole(), True),
                       Rule.Rule(App.App(CHIT1, [App.App(CONS2,
                                                         [hole(), hole()])]),
                                 hole(), True)]

cat2_templates = [
    Rule.Rule(App.App(CAT2, [hole(), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [hole(), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [hole(), App.App(CONS2, [hole(), hole()])]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [f(NIL), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [f(NIL), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [f(NIL), App.App(CONS2, [hole(), hole()])]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [App.App(CONS2, [hole(), hole()]), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [App.App(CONS2, [hole(), hole()]), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(CAT2, [App.App(CONS2, [hole(), hole()]),
                             App.App(CONS2, [hole(), hole()])]),
              hole(),
              True)]

count2_templates = [
    Rule.Rule(App.App(COUNT2, [hole(), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [hole(), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [hole(), App.App(CONS2, [hole(), hole()])]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [f(ZERO), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [f(ZERO), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [f(ZERO), App.App(CONS2, [hole(), hole()])]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [App.App(SUCC1, [hole()]), hole()]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [App.App(SUCC1, [hole()]), f(NIL)]),
              hole(),
              True),
    Rule.Rule(App.App(COUNT2, [App.App(SUCC1, [hole()]),
                               App.App(CONS2, [hole(), hole()])]),
              hole(),
              True)]

count31_templates = [Rule.Rule(App.App(COUNT31, [hole()]),
                               hole(), True),
                     Rule.Rule(App.App(COUNT31, [f(NIL)]),
                               hole(), True),
                     Rule.Rule(App.App(COUNT31, [App.App(CONS2,
                                                         [hole(), hole()])]),
                               hole(), True)]


e1_head1_templates = [Rule.Rule(App.App(HEAD1, [hole()]),
                                hole(), True),
                      Rule.Rule(App.App(HEAD1, [f(NIL)]),
                                hole(), True),
                      Rule.Rule(App.App(HEAD1, [App.App(CONS2,
                                                        [hole(), hole()])]),
                                hole(), True)]

e1_const1_templates = [Rule.Rule(App.App(CONST1, [hole()]),
                                 hole(), True),
                       Rule.Rule(App.App(CONST1, [f(NIL)]),
                                 hole(), True),
                       Rule.Rule(App.App(CONST1, [App.App(CONS2,
                                                          [hole(), hole()])]),
                                 hole(), True)]

e1_sum1_templates = [Rule.Rule(App.App(SUM1, [hole()]),
                               hole(), True),
                     Rule.Rule(App.App(SUM1, [f(NIL)]),
                               hole(), True),
                     Rule.Rule(App.App(SUM1, [App.App(CONS2,
                                                      [hole(), hole()])]),
                               hole(), True)]

e1_increment1_templates = [Rule.Rule(App.App(INCREMENT1, [hole()]),
                                     hole(), True),
                           Rule.Rule(App.App(INCREMENT1, [f(NIL)]),
                                     hole(), True),
                           Rule.Rule(App.App(INCREMENT1, [App.App(CONS2,
                                                                  [hole(),
                                                                   hole()])]),
                                     hole(), True)]

e1_sort1_templates = [Rule.Rule(App.App(SORT1, [hole()]),
                                hole(), True),
                      Rule.Rule(App.App(SORT1, [f(NIL)]),
                                hole(), True),
                      Rule.Rule(App.App(SORT1, [App.App(CONS2,
                                                        [hole(),
                                                         hole()])]),
                                hole(), True)]

e1_length1_templates = [Rule.Rule(App.App(LENGTH1, [hole()]),
                                  hole(), True),
                        Rule.Rule(App.App(LENGTH1, [f(NIL)]),
                                  hole(), True),
                        Rule.Rule(App.App(LENGTH1, [App.App(CONS2,
                                                            [hole(),
                                                             hole()])]),
                                  hole(), True)]

e1_deduplicate1_templates = [Rule.Rule(App.App(DEDUPLICATE1, [hole()]),
                                       hole(), True),
                             Rule.Rule(App.App(DEDUPLICATE1, [f(NIL)]),
                                       hole(), True),
                             Rule.Rule(App.App(DEDUPLICATE1,
                                               [App.App(CONS2,
                                                        [hole(),
                                                         hole()])]),
                                       hole(), True)]

e1_cumsum1_templates = [Rule.Rule(App.App(CUMSUM1, [hole()]),
                                  hole(), True),
                        Rule.Rule(App.App(CUMSUM1, [f(NIL)]),
                                  hole(), True),
                        Rule.Rule(App.App(CUMSUM1,
                                          [App.App(CONS2,
                                                   [hole(),
                                                    hole()])]),
                                  hole(), True)]

e1_filter_even1_templates = [
    Rule.Rule(App.App(FILTER_EVEN1, [hole()]),
              hole(), True),
    Rule.Rule(App.App(FILTER_EVEN1, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(FILTER_EVEN1, [App.App(CONS2, [hole(), hole()])]),
              hole(), True)]

e1_index_in_head1_templates = [
    Rule.Rule(App.App(IIH1, [hole()]),
              hole(), True),
    Rule.Rule(App.App(IIH1, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(IIH1, [App.App(CONS2,
                                     [hole(),
                                      hole()])]),
              hole(), True)]

e1_compare_head_and_sum_of_tail1_templates = [
    Rule.Rule(App.App(CHASOT1, [hole()]),
              hole(), True),
    Rule.Rule(App.App(CHASOT1, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(CHASOT1, [App.App(CONS2,
                                        [hole(),
                                         hole()])]),
              hole(), True)]


e1_count31_templates = [
    Rule.Rule(App.App(COUNT31, [hole()]),
              hole(), True),
    Rule.Rule(App.App(COUNT31, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(COUNT31, [App.App(CONS2,
                                        [hole(),
                                         hole()])]),
              hole(), True)]


e2_head1_templates = [
    Rule.Rule(App.App(HEAD1, [hole()]),
              hole(), True),
    Rule.Rule(App.App(HEAD1, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(HEAD1, [App.App(CONS2,
                                      [hole(), hole()])]),
              hole(), True)]

e2_tail1_templates = [
    Rule.Rule(App.App(TAIL1, [hole()]),
              hole(), True),
    Rule.Rule(App.App(TAIL1, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(TAIL1, [App.App(CONS2,
                                      [hole(), hole()])]),
              hole(), True)]

e2_count31_templates = [
    Rule.Rule(App.App(COUNT31, [hole()]),
              hole(), True),
    Rule.Rule(App.App(COUNT31, [f(NIL)]),
              hole(), True),
    Rule.Rule(App.App(COUNT31, [App.App(CONS2,
                                        [hole(), hole()])]),
              hole(), True)]

e2_good_chit1_templates = [
    Rule.Rule(App.App(CHIT1, [hole()]),
              hole(), True)]

e2_bad_chit1_templates = [
    Rule.Rule(App.App(CHIT1, [hole()]),
              hole(), True)]
