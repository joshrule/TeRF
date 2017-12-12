import copy
import pytest


@pytest.fixture(scope="module")
def objs():
    import TeRF.Types.Atom as Atom
    import TeRF.Types.Variable as Variable
    reload(Atom)
    reload(Variable)
    a = Variable.Variable('a')
    b = Variable.Variable('b')
    a2 = Variable.Variable('a')
    return(a, b, a2)


def test_variable_repr_a(objs):
    a, b, a2 = objs
    assert repr(a) == 'Variable(name=\'a\', identity=0)'


def test_variable_repr_b(objs):
    a, b, a2 = objs
    assert repr(b) == 'Variable(name=\'b\', identity=1)'


def test_variable_repr_a2(objs):
    a, b, a2 = objs
    assert repr(a2) == 'Variable(name=\'a\', identity=2)'


def test_variable_str_a(objs):
    a, b, a2 = objs
    assert str(a) == 'a_'


def test_variable_str_b(objs):
    a, b, a2 = objs
    assert str(b) == 'b_'


def test_variable_str_a2(objs):
    a, b, a2 = objs
    assert str(a2) == 'a_'


def test_variable_a_eq_a(objs):
    a, b, a2 = objs
    assert (a == a) is True


def test_variable_a_eq_copy_a(objs):
    a, b, a2 = objs
    assert (a == copy.copy(a)) is True


def test_variable_a_eq_deepcopy_a(objs):
    a, b, a2 = objs
    assert (a == copy.deepcopy(a)) is True


def test_variable_a_eq_b(objs):
    a, b, a2 = objs
    assert (a == b) is False


def test_variable_a_eq_a2(objs):
    a, b, a2 = objs
    assert (a == a2) is False


def test_variable_b_eq_a2(objs):
    a, b, a2 = objs
    assert (b == a2) is False


def test_variable_hash_a(objs):
    a, b, a2 = objs
    assert hash(a) == hash(('a', 0))


def test_variable_hash_a2(objs):
    a, b, a2 = objs
    assert hash(a2) == hash(('a', 2))


def test_variable_a_ne_a(objs):
    a, b, a2 = objs
    assert (a != a) is False


def test_variable_a_ne_b(objs):
    a, b, a2 = objs
    assert (a != b) is True


def test_variable_a_ne_a2(objs):
    a, b, a2 = objs
    assert (a != a2) is True
