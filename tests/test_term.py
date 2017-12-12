import copy
import pytest


@pytest.fixture(scope="module")
def a_and_b():
    import TeRF.Types.Term as Term
    a = Term.Term(0)
    b = Term.Term(1)
    return a, b


def test_term_repr_a(a_and_b):
    a, b = a_and_b
    assert repr(a) == 'Term(head=0)'


def test_term_repr_b(a_and_b):
    a, b = a_and_b
    assert repr(b) == 'Term(head=1)'


def test_term_str_a(a_and_b):
    a, b = a_and_b
    assert str(a) == 'Term(head=0)'


def test_term_str_b(a_and_b):
    a, b = a_and_b
    assert str(b) == 'Term(head=1)'


def test_term_a_eq_a(a_and_b):
    a, b = a_and_b
    assert (a == a) is True


def test_term_a_eq_copy_a(a_and_b):
    a, b = a_and_b
    assert (a == copy.copy(a)) is True


def test_term_a_eq_deepcopy_a(a_and_b):
    a, b = a_and_b
    assert (a == copy.deepcopy(a)) is True


def test_term_a_eq_b(a_and_b):
    a, b = a_and_b
    assert (a == b) is False


def test_term_hash_a(a_and_b):
    a, b = a_and_b
    assert hash(a) == hash((0,))


def test_term_a_ne_a(a_and_b):
    a, b = a_and_b
    assert (a != a) is False


def test_term_a_ne_b(a_and_b):
    a, b = a_and_b
    assert (a != b) is True


def test_term_len_a(a_and_b):
    a, b = a_and_b
    assert len(a) == 1


def test_term_len_b(a_and_b):
    a, b = a_and_b
    assert len(b) == 1
