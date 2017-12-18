import pytest
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Algorithms.Sampling as s
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind
import numpy as np


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

    return {o['NIL']: TBind.TBind(vC, List(vC)),
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
            variables['Z']: vH}


def test_sampling_1(typesystem, capsys):
    nat = TOp.TOp('NAT', [])
    for _ in xrange(20):
        term, _, _ = s.sample_term(nat, typesystem)
        # with capsys.disabled():
        #     print te.to_string(term)
        assert term is not None


def test_sampling_2(operators, variables, typesystem, capsys):
    o = operators
    v = variables
    nat = TOp.TOp('NAT', [])
    natlist = TOp.TOp('LIST', [nat])
    del typesystem[o['ID']]
    del typesystem[o['HEAD']]
    del typesystem[v['X']]
    del typesystem[v['Y']]
    del typesystem[v['Z']]
    for _ in xrange(20):
        term, _, _ = s.sample_term(natlist, typesystem, max_d=5)
        # with capsys.disabled():
        #     print te.to_string(term)
        assert term is not None


def test_sampling_3(operators, variables, typesystem, capsys):
    o = operators
    v = variables
    nat = TOp.TOp('NAT', [])
    del typesystem[o['ID']]
    del typesystem[o['HEAD']]
    del typesystem[v['X']]
    del typesystem[v['Y']]
    del typesystem[v['Z']]
    for _ in xrange(20):
        term, _, _ = s.sample_term(nat, typesystem, invent=True, max_d=5)
        # with capsys.disabled():
        #    print te.to_string(term)
        assert term is not None


def test_sampling_4(operators, variables, typesystem, capsys):
    o = operators
    v = variables
    nat = TOp.TOp('NAT', [])
    natlist = TOp.TOp('LIST', [nat])
    del typesystem[o['ID']]
    del typesystem[o['HEAD']]
    del typesystem[v['X']]
    del typesystem[v['Y']]
    del typesystem[v['Z']]
    for _ in xrange(20):
        term, _, _ = s.sample_term(natlist, typesystem, invent=True, max_d=5)
        # with capsys.disabled():
        #    print te.to_string(term)
        assert term is not None


def test_lp_1(operators, variables, typesystem):
    v = variables
    nat = TOp.TOp('NAT', [])
    term = v['X']
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=False, max_d=5)
    assert np.round(1./np.exp(lp)) == 8.0


def test_lp_2(makers, operators, typesystem):
    f, g, h, j, k = makers
    o = operators
    nat = TOp.TOp('NAT', [])
    term = f(o['ONE'])
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=False, max_d=5)
    assert np.round(1./np.exp(lp)) == 8.0


def test_lp_3(operators, variables, typesystem):
    v = variables
    nat = TOp.TOp('NAT', [])
    term = v['X']
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=True, max_d=5)
    assert np.round(1./np.exp(lp)) == 9.0


def test_lp_4(makers, operators, typesystem):
    f, g, h, j, k = makers
    o = operators
    nat = TOp.TOp('NAT', [])
    term = f(o['ONE'])
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=True, max_d=5)
    assert np.round(1./np.exp(lp)) == 9.0


def test_lp_5(makers, operators, typesystem):
    f, g, h, j, k = makers
    o = operators
    nat = TOp.TOp('NAT', [])
    term = h(o['HEAD'], o['NIL'])
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=False, max_d=5)
    assert np.round(1./np.exp(lp)) == (8.0 * 6.0 * 5.0)


def test_lp_6(makers, operators, typesystem):
    f, g, h, j, k = makers
    o = operators
    nat = TOp.TOp('NAT', [])
    term = h(o['HEAD'], o['NIL'])
    lp, _, _ = s.lp_term(term, nat, typesystem, invent=True, max_d=5)
    assert np.round(1./np.exp(lp)) == (9.0 * 7.0 * 6.0)


def test_sample_rule(operators, variables, typesystem, capsys):
    o = operators
    v = variables
    nat = TOp.TOp('NAT', [])
    del typesystem[o['ID']]
    del typesystem[v['X']]
    del typesystem[v['Y']]
    del typesystem[v['Z']]
    for _ in xrange(10):
        rule = s.sample_rule(nat, typesystem, invent=True, max_d=5)
        with capsys.disabled():
            print rule
        assert rule is not None


"""
TODO: I really should write tests for the other functions in this library
"""
