import TeRF.Types.Application as A
import TeRF.Types.CFGrammar as CFG
import TeRF.Types.Grammar as G
import TeRF.Types.LOT as LOT
import TeRF.Types.Operator as Op
import TeRF.Types.Rule as R
import TeRF.Types.Variable as V


def f(x, xs=None):
    if xs is None:
        xs = []
    return A.App(x, xs)


def g(x, y):
    return A.App(DOT, [x, y])


# make a bunch of primitives
START = Op.Operator('START', 0)
LIST = Op.Operator('list', 0)
NUMBER = Op.Operator('number', 0)
NIL = Op.Operator('nil', 0)
NEL = Op.Operator('nel', 0)
CONS = Op.Operator('cons', 0)
ZERO = Op.Operator('0', 0)
ONE = Op.Operator('1', 0)
TWO = Op.Operator('2', 0)
THREE = Op.Operator('3', 0)
DOT = Op.Operator('.', 2)
HEAD = Op.Operator('head', 0)

# make a few variables
X = V.Var('x')
Y = V.Var('y')
Z = V.Var('z')

# make an fPCFG for just the minimal list primitives and 0-3
list_fpcfg = CFG.FPCFG(primitives={START, LIST, NIL, CONS, DOT,
                                   NUMBER, ZERO, ONE, TWO, THREE})

# make an fPCFG for list primitives, including head
head_fpcfg = CFG.FPCFG(primitives={START, LIST, NUMBER, NIL, NEL, CONS,
                                   ZERO, ONE, TWO, THREE, DOT, HEAD},
                       start=f(START))

# make a PCFG for learning the syntax of lists
rule_START = R.Rule(f(START),
                    {f(NUMBER), f(ZERO), f(ONE), f(TWO), f(THREE),
                     f(LIST), f(NIL), f(CONS), g(f(START), f(START))})

list_pcfg = CFG.PCFG(rules={rule_START})

# make a PCFG for the head list problem, including head
rule_START = R.Rule(f(START), {f(LIST), f(NUMBER)})
rule_LIST = R.Rule(f(LIST), {f(NIL), f(NEL)})
rule_NEL = R.Rule(f(NIL), g(g(f(CONS), f(NUMBER)), f(LIST)))
rule_NUMBER = R.Rule(f(NUMBER), {f(ZERO), f(ONE), f(TWO), f(THREE)})
rule_head = R.Rule(f(NUMBER), g(f(HEAD), f(NEL)))

head_pcfg = CFG.PCFG(rules={rule_START, rule_LIST, rule_NEL,
                            rule_NUMBER, rule_head},
                     start=f(START))

# make a Grammar for list semantics
rule_LIST = R.Rule(f(LIST), {f(NIL), g(g(f(CONS), f(NUMBER)), f(LIST))})

list_g = G.Grammar(rules={rule_NUMBER, rule_LIST})

# make a Grammar for list semantics, including head
head_rule = R.Rule(g(f(HEAD), g(g(f(CONS), X), Y)), Y)

head_g = G.Grammar(rules={head_rule})

# make an LOT for learning to make lists
list_lot = LOT.LOT(primitives=list_fpcfg, syntax=list_pcfg, semantics=list_g)

# make an LOT for learning head
head_lot = LOT.LOT(primitives=head_fpcfg, syntax=head_pcfg, semantics=head_g)
