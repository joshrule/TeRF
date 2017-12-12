import copy
import pytest


@pytest.fixture(scope="module")
def atoms():
    import TeRF.Types.TypeOperator as TOp
    import TeRF.Types.TypeVariable as TVar
    reload(TOp)
    reload(TVar)

    x = TVar.TVar()
    Bool = TOp.TOp('Bool', [])
    Nat = TOp.TOp('Nat', [])
    List_of_Nat = TOp.TOp('List', [Nat])
    Bool_to_Bool1 = TOp.TOp('->', [Bool, Bool])
    Bool_to_Bool2 = TOp.TOp('->', [Bool, Bool])
    x_to_Bool = TOp.TOp('->', [x, Bool])
    Bool_to_Nat = TOp.TOp('->', [Bool, Nat])

    return (Bool, Nat, List_of_Nat, Bool_to_Bool1,
            Bool_to_Bool2, x_to_Bool, Bool_to_Nat, x)


def test_application_repr_b(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert repr(b) == 'TypeOperator(head=\'Nat\', args=[])'


def test_application_repr_c(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert repr(c) == ('TypeOperator(head=\'List\', args=['
                       'TypeOperator(head=\'Nat\', args=[])])')


def test_application_repr_d(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert repr(d) == ('TypeOperator(head=\'->\', args=['
                       'TypeOperator(head=\'Bool\', args=[]), '
                       'TypeOperator(head=\'Bool\', args=[])])')


def test_application_str_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(a) == 'Bool'


def test_application_str_b(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(b) == 'Nat'


def test_application_str_c(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(c) == 'List[Nat]'


def test_application_str_d(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(d) == '(Bool -> Bool)'


def test_application_str_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(e) == '(Bool -> Bool)'


def test_application_str_f(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(f) == '(v0 -> Bool)'


def test_application_str_g(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert str(g) == '(Bool -> Nat)'


def test_application_a_eq_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == a) is True


def test_application_a_eq_copy_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == copy.copy(a)) is True


def test_application_a_eq_deepcopy_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == copy.deepcopy(a)) is True


def test_application_a_eq_b(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == b) is False


def test_application_a_eq_c(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == c) is False


def test_application_a_eq_d(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == d) is False


def test_application_a_eq_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == e) is False


def test_application_a_eq_f(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == f) is False


def test_application_a_eq_g(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == g) is False


def test_application_a_eq_h(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a == h) is False


def test_application_d_eq_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (d == e) is True


def test_application_d_eq_f(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (d == f) is False


def test_application_d_eq_g(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (d == g) is False


def test_application_d_eq_h(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (d == h) is False


def test_application_hash_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(a) == hash(('Bool', ()))


def test_application_hash_b(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(b) == hash(('Nat', ()))


def test_application_hash_c(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(c) == hash(('List', (b,)))


def test_application_hash_d(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(d) == hash(('->', (a, a)))


def test_application_hash_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(e) == hash(('->', (a, a)))


def test_application_hash_f(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(f) == hash(('->', (h, a)))


def test_application_hash_g(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert hash(g) == hash(('->', (a, b)))


def test_application_a_ne_a(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != a) is False


def test_application_a_ne_b(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != b) is True


def test_application_a_ne_c(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != c) is True


def test_application_a_ne_d(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != d) is True


def test_application_a_ne_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != e) is True


def test_application_a_ne_f(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != f) is True


def test_application_a_ne_g(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != g) is True


def test_application_a_ne_h(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (a != h) is True


def test_application_d_ne_e(atoms):
    a, b, c, d, e, f, g, h = atoms
    assert (d != e) is False
