import copy
import pytest


@pytest.fixture(scope="module")
def atoms():
    import TeRF.Types.TypeOperator as TOp
    import TeRF.Types.TypeVariable as TVar
    reload(TOp)
    reload(TVar)

    x = TVar.TVar()
    y = TVar.TVar()
    Bool = TOp.TOp('Bool', [])
    Nat = TOp.TOp('Nat', [])
    Bool_to_Nat = TOp.F(Bool, Nat)
    x_to_Bool = TOp.F(x, Bool)
    x_to_y = TOp.F(x, y)

    return (x, y, Bool, Nat, Bool_to_Nat, x_to_Bool, x_to_y)


@pytest.fixture(scope="module")
def bindings(atoms):
    import TeRF.Types.TypeBinding as TBind
    reload(TBind)
    x, y, b, n, bn, xb, xy = atoms    

    return (TBind.TBind(x, x),
            TBind.TBind(x, y),
            TBind.TBind(x, b),
            TBind.TBind(x, n),
            TBind.TBind(x, bn),
            TBind.TBind(x, xb),
            TBind.TBind(x, xy),
            TBind.TBind(y, x),
            TBind.TBind(y, y))


def test_application_repr_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xx) == ('TypeBinding(variable=TypeVariable(id=0), '
                        'body=TypeVariable(id=0))')


def test_application_repr_xy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xy) == ('TypeBinding(variable=TypeVariable(id=0), '
                        'body=TypeVariable(id=1))')


def test_application_repr_xb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xb) == ('TypeBinding(variable=TypeVariable(id=0), '
                        'body=TypeOperator(head=\'Bool\', args=[]))')


def test_application_repr_xn(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xn) == ('TypeBinding(variable=TypeVariable(id=0), '
                        'body=TypeOperator(head=\'Nat\', args=[]))')


def test_application_repr_xbn(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xbn) == ('TypeBinding(variable=TypeVariable(id=0), '
                         'body=TypeOperator(head=\'->\', args=['
                         'TypeOperator(head=\'Bool\', args=[]), '
                         'TypeOperator(head=\'Nat\', args=[])]))')


def test_application_repr_xxb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xxb) == ('TypeBinding(variable=TypeVariable(id=0), '
                         'body=TypeOperator(head=\'->\', args=['
                         'TypeVariable(id=0), '
                         'TypeOperator(head=\'Bool\', args=[])]))')


def test_application_repr_xxy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(xxy) == ('TypeBinding(variable=TypeVariable(id=0), '
                         'body=TypeOperator(head=\'->\', args=['
                         'TypeVariable(id=0), '
                         'TypeVariable(id=1)]))')


def test_application_repr_yx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(yx) == ('TypeBinding(variable=TypeVariable(id=1), '
                        'body=TypeVariable(id=0))')


def test_application_repr_yy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert repr(yy) == ('TypeBinding(variable=TypeVariable(id=1), '
                        'body=TypeVariable(id=1))')


def test_application_str_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xx) == '()v0.v0'


def test_application_str_xy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xy) == '()v0.v1'


def test_application_str_xb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xb) == '()v0.Bool'


def test_application_str_xn(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xn) == '()v0.Nat'


def test_application_str_xbn(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xbn) == '()v0.(Bool -> Nat)'


def test_application_str_xxb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xxb) == '()v0.(v0 -> Bool)'


def test_application_str_xxy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(xxy) == '()v0.(v0 -> v1)'


def test_application_str_yx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(yx) == '()v1.v0'


def test_application_str_yy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert str(yy) == '()v1.v1'


def test_application_xx_eq_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xx) is True

def test_application_xx_eq_xy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xy) is False


def test_application_xx_eq_xb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xb) is False


def test_application_xx_eq_xbn(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xbn) is False


def test_application_xx_eq_xxb(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xxb) is False


def test_application_xx_eq_xxy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == xxy) is False


def test_application_xx_eq_yy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == yy) is False


def test_application_xy_eq_yx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xy == yx) is False


def test_application_xx_eq_copy_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == copy.copy(xx)) is True


def test_application_xx_eq_deepcopy_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx == copy.deepcopy(xx)) is True


def test_application_hash_xx(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xx) == hash((x, x))


def test_application_hash_xy(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xy) == hash((x, y))


def test_application_hash_xb(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xb) == hash((x, b))


def test_application_hash_xn(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xn) == hash((x, n))


def test_application_hash_xbn(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xbn) == hash((x, bn))


def test_application_hash_xxb(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xxb) == hash((x, xb_atom))


def test_application_hash_xxy(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy_atom = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(xxy) == hash((x, xy_atom))


def test_application_hash_yx(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(yx) == hash((y, x))


def test_application_hash_yy(atoms, bindings):
    x, y, b, n, bn, xb_atom, xy = atoms
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert hash(yy) == hash((y, y))


def test_application_xx_ne_xx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx != xx) is False


def test_application_xx_ne_xy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xx != xy) is True


def test_application_xbn_ne_xxy(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xbn != xxy) is True


def test_application_xy_ne_yx(bindings):
    xx, xy, xb, xn, xbn, xxb, xxy, yx, yy = bindings
    assert (xy != yx) is True
