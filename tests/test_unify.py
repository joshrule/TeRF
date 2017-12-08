import pytest
import TeRF.Algorithms.Unify as U


@pytest.fixture(scope="module")
def atoms():
    import TeRF.Types.Atom as Atom
    import TeRF.Types.Operator as Operator
    import TeRF.Types.Variable as Variable
    reload(Atom)
    reload(Operator)
    reload(Variable)

    dot = Operator.Operator('.', 2)
    A = Operator.Operator('A')
    B = Operator.Operator('B')
    C = Operator.Operator('C')
    x = Variable.Variable('x')
    y = Variable.Variable('y')

    return dot, A, B, C, x, y


@pytest.fixture(scope="module")
def terms(atoms):
    dot, A, B, C, x, y = atoms
    import TeRF.Types.Application as Application
    reload(Application)

    t = Application.Application(dot, [
        Application.Application(A, []),
        Application.Application(dot, [
            Application.Application(B, []),
            Application.Application(dot, [
                Application.Application(C, []),
                Application.Application(dot, [
                    Application.Application(A, []),
                    Application.Application(A, [])])])])])
    s = Application.Application(dot, [x, y])
    return s, t, x


def test_unify_free_vars_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.free_vars(x) == {x}


def test_unify_free_vars_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.free_vars(s) == {x, y}


def test_unify_free_vars_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.free_vars(t) == set()


def test_unify_unify_t_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(t, x)}) == {x: t}


def test_unify_unify_x_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(x, x)}) == {}


def test_unify_unify_t_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(t, t)}) == {}


def test_unify_unify_x_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(x, t)}) == {x: t}


def test_unify_match_x_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(x, t)}, kind='match') == {x: t}


def test_unify_match_t_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(t, x)}, kind='match') is None


def test_unify_match_s_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(s, t)}, kind='match') == {x: t.args[0],
                                               y: t.args[1]}


def test_unify_match_t_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(t, s)}, kind='match') is None


def test_unify_unify_t_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, x = terms
    assert U.unify({(t, s)}) == {x: t.args[0],
                                 y: t.args[1]}
