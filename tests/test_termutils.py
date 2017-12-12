import copy
import pytest
import TeRF.Algorithms.TermUtils as TU


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
                Application.Application(dot, [x, y])])])])
    return t, x


def test_termutils_atoms_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.atoms(t) == set(atoms)


def test_termutils_atoms_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.atoms(x) == {x}


def test_termutils_operators_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.operators(t) == {dot, A, B, C}


def test_termutils_operators_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.operators(x) == set()


def test_termutils_variables_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.variables(t) == {x, y}


def test_termutils_variables_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.variables(x) == {x}


def test_termutils_places_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.places(t) == [[],
                            [0],
                            [1],
                            [1, 0],
                            [1, 1],
                            [1, 1, 0],
                            [1, 1, 1],
                            [1, 1, 1, 0],
                            [1, 1, 1, 1]]


def test_termutils_places_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.places(x) == [[]]


def test_termutils_subterms_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert list(TU.subterms(t)) == [t,
                                    t.args[0],
                                    t.args[1],
                                    t.args[1].args[0],
                                    t.args[1].args[1],
                                    t.args[1].args[1].args[0],
                                    t.args[1].args[1].args[1],
                                    t.args[1].args[1].args[1].args[0],
                                    t.args[1].args[1].args[1].args[1]]


def test_termutils_subterms_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert list(TU.subterms(x)) == [x]


def test_termutils_subterm_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.subterm(t, []) == t


def test_termutils_subterm_t_0(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.subterm(t, [0]) == t.args[0]


def test_termutils_subterm_t_1110(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.subterm(t, [1]*3+[0]) == t.args[1].args[1].args[1].args[0]


def test_termutils_subterm_t_101(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    with pytest.raises(ValueError):
        TU.subterm(t, [1, 0, 1])


def test_termutils_subterm_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.subterm(x, []) == x


def test_termutils_subterm_x_0(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    with pytest.raises(ValueError):
        TU.subterm(x, [0])


def test_termutils_replace_t_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.replace(t, [], x) == x


def test_termutils_replace_x_y(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.replace(x, [], y) == y


def test_termutils_replace_t_110_A(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    u = copy.deepcopy(t)
    u.args[1].args[1].args[0] = x
    assert TU.replace(t, [1, 1, 0], x) == u


def test_termutils_to_string_t_0(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.to_string(t, 0) == 'A (B (C (x_ y_)))'


def test_termutils_to_string_t_1(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.to_string(t, 1) == '(A (B (C (x_ y_))))'


def test_termutils_to_string_t_2(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.to_string(t, 1) == '(A (B (C (x_ y_))))'


def test_termutils_to_string_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.to_string(x) == 'x_'


def test_termutils_rename_variables_t(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    string0 = 'A (B (C (v0_ v1_)))'
    string1 = 'A (B (C (v1_ v0_)))'
    value = TU.to_string(TU.rename_variables(t))
    assert value == string0 or value == string1


def test_termutils_rename_variables_x(atoms, terms):
    dot, A, B, C, x, y = atoms
    t, x = terms
    assert TU.to_string(TU.rename_variables(x)) == 'v0_'
