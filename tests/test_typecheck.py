import pytest
import TeRF.Miscellaneous as misc
import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.Typecheck as tc
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind


@pytest.fixture(scope='module')
def makers(operators):
    import TeRF.Types.Application as App

    DOT = operators['DOT']

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

    return f, g, h, j, k


@pytest.fixture(scope='module')
def operators():
    import TeRF.Types.Operator as Op

    return {'DOT': Op.Op('.', 2),
            'NIL': Op.Op('nil', 0),
            'CONS': Op.Op('cons', 0),
            'ZERO': Op.Op('0', 0),
            'ONE': Op.Op('1', 0),
            'TWO': Op.Op('2', 0),
            'THREE': Op.Op('3', 0),
            'HEAD': Op.Op('head', 0),
            'PAIR': Op.Op('pr', 0),
            'ID': Op.Op('id', 0),
            'TAIL': Op.Op('tail', 0)}


@pytest.fixture(scope='module')
def variables():
    import TeRF.Types.Variable as Var
    reload(Var)
    return {'X': Var.Var('X'),
            'Y': Var.Var('Y'),
            'Z': Var.Var('Z')}


@pytest.fixture
def typesystem(makers, operators, variables):
    f, g, h, j, k = makers
    o = operators

    NAT = TOp.TOp('NAT', [])
    vA = TVar.TVar()
    vB = TVar.TVar()
    vC = TVar.TVar()
    vD = TVar.TVar()
    vE = TVar.TVar()
    vF = TVar.TVar()
    vG = TVar.TVar()
    vH = TVar.TVar()
    vI = TVar.TVar()

    class List(TOp.TOp):
        def __init__(self, alpha_type):
            super(List, self).__init__('LIST', [alpha_type])

    class Pair(TOp.TOp):
        def __init__(self, alpha_type, beta_type):
            super(Pair, self).__init__('PAIR', [alpha_type, beta_type])

    env = misc.edict({
        o['NIL']: TBind.TBind(vC, List(vC)),
        o['ZERO']: NAT,
        o['ONE']: NAT,
        o['TWO']: NAT,
        o['THREE']: NAT,
        o['CONS']: TBind.TBind(vD,
                               ty.function(vD,
                                           ty.function(List(vD),
                                                       List(vD)))),
        o['DOT']: TBind.TBind(vA,
                              TBind.TBind(vB,
                                          ty.function(
                                              ty.function(vA, vB),
                                              ty.function(vA, vB)))),
        o['ID']: TBind.TBind(vC, ty.function(vC, vC)),
        o['PAIR']: TBind.TBind(vF,
                               TBind.TBind(
                                   vG,
                                   ty.function(
                                       vF,
                                       ty.function(
                                           vG,
                                           Pair(vF, vG))))),
        o['HEAD']: TBind.TBind(vE, ty.function(List(vE), vE)),
        variables['X']: vH,
        variables['Y']: vI,
        variables['Z']: vH})
    env.fvs = ty.free_vars_in_env(env)
    return env


def test_typecheck_1(makers, operators, variables, typesystem):
    term = variables['X']
    result = tc.typecheck(term, typesystem, {})
    expected = typesystem[variables['X']]
    assert ty.alpha(result, expected) is not None


def test_typecheck_2(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = f(o['NIL'])
    result = tc.typecheck(term, typesystem, {})
    expected = typesystem[o['NIL']]
    assert ty.alpha(result, expected) is not None


def test_typecheck_3(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = f(o['CONS'])
    result = tc.typecheck(term, typesystem, {})
    expected = typesystem[o['CONS']]
    assert ty.alpha(result, expected) is not None


def test_typecheck_4(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = h(o['HEAD'], o['NIL'])
    result = tc.typecheck(term, typesystem, {})
    x = TVar.TVar()
    expected = TBind.TBind(x, x)
    assert ty.alpha(result, expected) is not None


def test_typecheck_5(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = h(o['CONS'], o['ONE'])
    result = tc.typecheck(term, typesystem, {})
    natlist = TOp.TOp('LIST', [TOp.TOp('NAT', [])])
    expected = ty.function(natlist, natlist)
    assert ty.alpha(result, expected) is not None


def test_typecheck_6(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = j(o['CONS'], v['X'])
    sub = {}
    result, sub = tc.typecheck_full(term, typesystem, sub)
    x = ty.substitute([typesystem[v['X']]], sub)[0]
    expected = TOp.TOp('->', [TOp.TOp('LIST', [x]),
                              TOp.TOp('LIST', [x])])
    print 'result', result
    print 'expected', expected
    assert ty.alpha(result, expected) is not None


def test_typecheck_7(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(j(o['CONS'], v['X']), v['X'])
    with pytest.raises(ValueError):
        print tc.typecheck(term, typesystem, {})


def test_typecheck_8(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(h(o['CONS'], o['ONE']), v['X'])
    result = tc.typecheck(term, typesystem, {})
    expected = TOp.TOp('LIST', [TOp.TOp('NAT', [])])
    assert ty.alpha(result, expected) is not None


def test_typecheck_9(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = k(h(o['CONS'], o['ONE']), o['TWO'])
    with pytest.raises(ValueError):
        print tc.typecheck(term, typesystem, {})


def test_typecheck_10(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(h(o['CONS'], o['ONE']), k(j(o['CONS'], v['X']), o['NIL']))
    result = tc.typecheck(term, typesystem, {})
    expected = TOp.TOp('LIST', [TOp.TOp('NAT', [])])
    assert ty.alpha(result, expected) is not None


def test_typecheck_11(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = j(o['HEAD'],
             g(j(o['CONS'],
               h(o['HEAD'], o['NIL'])),
             k(h(o['CONS'], o['TWO']), o['NIL'])))
    result = tc.typecheck(term, typesystem, {})
    expected = TOp.TOp('NAT', [])
    assert ty.alpha(result, expected) is not None


def test_typecheck_12(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = k(j(o['CONS'], v['X']), o['NIL'])
    sub = {}
    result, sub = tc.typecheck_full(term, typesystem, sub)
    x = ty.substitute([typesystem[v['X']]], sub)[0]
    expected = TOp.TOp('LIST', [x])
    assert ty.alpha(result, expected) is not None


def test_typecheck_13(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = k(h(o['PAIR'], o['NIL']), o['ZERO'])
    result = tc.typecheck(term, typesystem, {})
    x = TVar.TVar()
    expected = TBind.TBind(x, TOp.TOp('PAIR', [TOp.TOp('LIST', [x]),
                                               TOp.TOp('NAT', [])]))
    assert ty.alpha(result, expected) is not None


def test_typecheck_14(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    term = g(j(o['PAIR'], h(o['ID'], o['NIL'])), h(o['ID'], o['ZERO']))
    result = tc.typecheck(term, typesystem, {})
    x = TVar.TVar()
    expected = TBind.TBind(x, TOp.TOp('PAIR', [TOp.TOp('LIST', [x]),
                                               TOp.TOp('NAT', [])]))
    assert ty.alpha(result, expected) is not None


def test_typecheck_15(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(j(o['CONS'], v['X']), v['Y'])
    sub = {}
    result, sub = tc.typecheck_full(term, typesystem, sub)
    x = ty.substitute([typesystem[v['X']]], sub)[0]
    expected = TOp.TOp('LIST', [x])
    print 'result', result
    print 'expected', expected
    assert ty.alpha(result, expected) is not None


def test_typecheck_16(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(j(o['CONS'], v['X']), v['Z'])
    with pytest.raises(ValueError):
        print tc.typecheck(term, typesystem, {})


def test_typecheck_17(makers, operators, variables, typesystem):
    f, g, h, j, k = makers
    o = operators
    v = variables
    term = g(h(o['CONS'], o['ONE']), k(j(o['CONS'], v['X']), o['NIL']))
    nat = TOp.TOp('NAT', [])
    natlist = TOp.TOp('LIST', [nat])
    types = [natlist,
             TOp.TOp('->', [natlist, natlist]),
             typesystem[o['CONS']],
             nat,
             natlist,
             TOp.TOp('->', [natlist, natlist]),
             typesystem[o['CONS']],
             nat,
             typesystem[o['NIL']]]
    sub = {}
    for subterm, expected in zip(te.subterms(term), types):
        result, sub = tc.typecheck_full(subterm, typesystem, sub)
        assert ty.alpha(result, expected) is not None
