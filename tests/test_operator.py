import copy
import pytest


@pytest.fixture(scope="module")
def objs():
    import TeRF.Types.Atom as Atom
    import TeRF.Types.Operator as Operator
    reload(Atom)
    reload(Operator)
    a = Operator.Operator('A')
    b = Operator.Operator('B')
    a2 = Operator.Operator('A', 2)
    return(a, b, a2)


def test_operator_repr_a(objs):
    a, b, a2 = objs
    assert repr(a) == 'Operator(name=\'A\', arity=0, identity=0)'


def test_operator_repr_b(objs):
    a, b, a2 = objs
    assert repr(b) == 'Operator(name=\'B\', arity=0, identity=1)'


def test_operator_repr_a2(objs):
    a, b, a2 = objs
    assert repr(a2) == 'Operator(name=\'A\', arity=2, identity=2)'


def test_operator_str_a(objs):
    a, b, a2 = objs
    assert str(a) == 'A'


def test_operator_str_b(objs):
    a, b, a2 = objs
    assert str(b) == 'B'


def test_operator_str_a2(objs):
    a, b, a2 = objs
    assert str(a2) == 'A'


def test_operator_a_eq_a(objs):
    a, b, a2 = objs
    assert (a == a) is True


def test_operator_a_eq_copy_a(objs):
    a, b, a2 = objs
    assert (a == copy.copy(a)) is True


def test_operator_a_eq_deepcopy_a(objs):
    a, b, a2 = objs
    assert (a == copy.deepcopy(a)) is True


def test_operator_a_eq_b(objs):
    a, b, a2 = objs
    assert (a == b) is False


def test_operator_a_eq_a2(objs):
    a, b, a2 = objs
    assert (a == a2) is False


def test_operator_b_eq_a2(objs):
    a, b, a2 = objs
    assert (b == a2) is False


def test_operator_hash_a(objs):
    a, b, a2 = objs
    assert hash(a) == hash(('A', 0, 0))


def test_operator_hash_a2(objs):
    a, b, a2 = objs
    assert hash(a2) == hash(('A', 2, 2))


def test_operator_a_ne_a(objs):
    a, b, a2 = objs
    assert (a != a) is False


def test_operator_a_ne_b(objs):
    a, b, a2 = objs
    assert (a != b) is True


def test_operator_a_ne_a2(objs):
    a, b, a2 = objs
    assert (a != a2) is True
