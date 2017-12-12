import copy
import pytest


@pytest.fixture(scope="module")
def a_and_b():
    import TeRF.Types.Atom as Atom
    reload(Atom)
    a = Atom.Atom()
    b = Atom.Atom()
    return a, b


def test_atom_repr_a(a_and_b):
    a, b = a_and_b
    assert repr(a) == 'Atom(identity=0)'


def test_atom_str_b(a_and_b):
    a, b = a_and_b
    assert str(b) == 'atom_1'


def test_atom_repr_b(a_and_b):
    a, b = a_and_b
    assert repr(b) == 'Atom(identity=1)'


def test_atom_str_a(a_and_b):
    a, b = a_and_b
    assert str(a) == 'atom_0'


def test_atom_a_eq_a(a_and_b):
    a, b = a_and_b
    assert (a == a) is True


def test_atom_a_eq_copy_a(a_and_b):
    a, b = a_and_b
    assert (a == copy.copy(a)) is True


def test_atom_a_eq_deepcopy_a(a_and_b):
    a, b = a_and_b
    assert (a == copy.deepcopy(a)) is True


def test_atom_a_eq_b(a_and_b):
    a, b = a_and_b
    assert (a == b) is False


def test_atom_hash_a(a_and_b):
    a, b = a_and_b
    assert hash(a) == hash((0,))


def test_atom_a_ne_a(a_and_b):
    a, b = a_and_b
    assert (a != a) is False


def test_atom_a_ne_b(a_and_b):
    a, b = a_and_b
    assert (a != b) is True
