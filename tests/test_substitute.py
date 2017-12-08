import pytest
import TeRF.Algorithms.Substitute as S
import TeRF.Types.Application as Application


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
    reload(Application)

    s = Application.Application(dot, [x, y])
    t = Application.Application(dot, [
        Application.Application(A, []),
        Application.Application(dot, [
            x,
            Application.Application(dot, [
                y,
                Application.Application(dot, [
                    Application.Application(A, []),
                    Application.Application(A, [])])])])])
    u = Application.Application(dot, [
        Application.Application(B, []),
        Application.Application(B, [])])
    v = Application.Application(A, [])
    return s, t, u, v


def test_substitute_x_y_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(s, {x: y}) == Application.Application(dot, [y, y])


def test_substitute_y_x_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(s, {y: x}) == Application.Application(dot, [x, x])


def test_substitute_x_x_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(s, {x: x}) == s


def test_substitute_x_u_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(s, {x: u}) == Application.Application(dot, [u, y])


def test_substitute_x_u_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(t, {x: u}) == Application.Application(dot, [
        v,
        Application.Application(dot, [
            u,
            Application.Application(dot, [
                y,
                Application.Application(dot, [v, v])])])])


def test_substitute_x_u_u(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(u, {x: u}) == u


def test_substitute_x_u_v(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(v, {x: u}) == v


def test_substitute_x_s_s(atoms, terms):
    dot, A, B, C, x, y = atoms
    s, t, u, v = terms
    assert S.substitute(s, {x: s}) == Application.Application(dot, [s, y])
