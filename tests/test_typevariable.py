import copy
import pytest


@pytest.fixture(scope="module")
def tvars():
    import TeRF.Types.TypeVariable as TVar
    reload(TVar)
    a = TVar.TVar()
    b = TVar.TVar()
    return a, b


def test_typevariable_repr_a(tvars):
    a, b = tvars
    assert repr(a) == 'TypeVariable(id=0)'


def test_typevariable_repr_b(tvars):
    a, b = tvars
    assert repr(b) == 'TypeVariable(id=1)'


def test_typevariable_str_a(tvars):
    a, b = tvars
    assert str(a) == 'v0'


def test_typevariable_str_b(tvars):
    a, b = tvars
    assert str(b) == 'v1'


def test_typevariable_a_eq_a(tvars):
    a, b = tvars
    assert (a == a) is True


def test_typevariable_a_eq_copy_a(tvars):
    a, b = tvars
    assert (a == copy.copy(a)) is True


def test_typevariable_a_eq_deepcopy_a(tvars):
    a, b = tvars
    assert (a == copy.deepcopy(a)) is True


def test_typevariable_a_eq_b(tvars):
    a, b = tvars
    assert (a == b) is False


def test_typevariable_hash_a(tvars):
    a, b = tvars
    assert hash(a) == hash((0,))


def test_typevariable_hash_b(tvars):
    a, b = tvars
    assert hash(b) == hash((1,))


def test_typevariable_a_ne_a(tvars):
    a, b = tvars
    assert (a != a) is False


def test_typevariable_a_ne_b(tvars):
    a, b = tvars
    assert (a != b) is True
