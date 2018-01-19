import pytest
import TeRF.Miscellaneous as misc
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Types.TypeBinding as TBind
import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.Variable as Var


@pytest.fixture(scope="module")
def atoms():
    reload(TVar)

    x = TVar.TVar()
    y = TVar.TVar()
    Bool = TOp.TOp('Bool', [])
    Nat = TOp.TOp('Nat', [])

    return x, y, Bool, Nat


def test_multi_argument_function_var(atoms):
    x, y, b, n = atoms
    result = ty.multi_argument_function([x, y, b, n])
    r = ty.result_type(result)
    assert isinstance(r, TVar.TVar) and r != x != y and \
        result == TOp.TOp('->',
                          [x, TOp.TOp('->',
                                      [y, TOp.TOp('->',
                                                  [b, TOp.TOp('->',
                                                              [n, r])])])])


def test_multi_argument_function_arg(atoms):
    x, y, b, n = atoms
    result = ty.multi_argument_function([b, n, x], y)
    assert result == TOp.TOp('->',
                             [b, TOp.TOp('->',
                                         [n, TOp.TOp('->',
                                                     [x, y])])])


def test_function_b_n(atoms):
    x, y, b, n = atoms
    assert ty.function(b, n) == TOp.TOp('->', [b, n])


def test_function_b_x(atoms):
    x, y, b, n = atoms
    assert ty.function(b, x) == TOp.TOp('->', [b, x])


def test_function_y_x(atoms):
    x, y, b, n = atoms
    assert ty.function(y, x) == TOp.TOp('->', [y, x])


def test_is_function_y_x(atoms):
    x, y, b, n = atoms
    assert ty.is_function(ty.function(y, x)) is True


def test_is_function_b_x(atoms):
    x, y, b, n = atoms
    assert ty.is_function(ty.function(b, x)) is True


def test_is_function_y(atoms):
    x, y, b, n = atoms
    assert ty.is_function(y) is False


def test_is_function_b(atoms):
    x, y, b, n = atoms
    assert ty.is_function(b) is False


def test_is_function_list_b(atoms):
    x, y, b, n = atoms
    assert ty.is_function(TOp.TOp('LIST', [b])) is False


def test_result_type_x(atoms):
    x, y, b, n = atoms
    with pytest.raises(ValueError):
        ty.result_type(x)


def test_result_type_b(atoms):
    x, y, b, n = atoms
    with pytest.raises(ValueError):
        ty.result_type(b)


def test_result_type_id(atoms):
    x, y, b, n = atoms
    with pytest.raises(ValueError):
        ty.result_type(TBind.TBind(x, TOp.TOp('->', [x, x])))


def test_result_type_bn(atoms):
    x, y, b, n = atoms
    assert ty.result_type(TOp.TOp('->', [b, n])) == n


def test_result_type_bnx(atoms):
    x, y, b, n = atoms
    assert ty.result_type(TOp.TOp('->', [b, TOp.TOp('->', [n, x])])) == x


def test_result_type_bnlistx(atoms):
    x, y, b, n = atoms
    result = ty.result_type(TOp.TOp('->',
                                    [b, TOp.TOp('->',
                                                [n, TOp.TOp('LIST',
                                                            [x])])]))
    expected = TOp.TOp('LIST', [x])
    assert result == expected


def test_generalize_x(atoms):
    x, y, b, n = atoms
    t1 = ty.generalize(x)
    assert isinstance(t1, TBind.TBind) and \
        (t1.variable == x != y) and \
        isinstance(t1.body, TVar.TVar) and \
        t1.variable == t1.body


def test_generalize_b(atoms):
    x, y, b, n = atoms
    t1 = ty.generalize(b)
    assert t1 == b


def test_generalize_x_x(atoms):
    x, y, b, n = atoms
    t1 = ty.generalize(x, {x})
    assert t1 == x


def test_generalize_xxy(atoms):
    x, y, b, n = atoms
    t1 = TBind.TBind(x, TOp.TOp('->', [x, y]))
    t2 = ty.generalize(t1)
    t3 = TBind.TBind(y, TBind.TBind(x, TOp.TOp('->', [x, y])))
    assert t2 == t3


def test_specialize_x(atoms):
    x, y, b, n = atoms
    assert ty.specialize_top(x) == x


def test_specialize_b(atoms):
    x, y, b, n = atoms
    assert ty.specialize_top(b) == b


def test_specialize_xx(atoms):
    x, y, b, n = atoms
    t1 = TOp.TOp('->', [x, x])
    assert ty.specialize_top(t1) == t1


def test_specialize_xx2(atoms):
    x, y, b, n = atoms
    t1 = TBind.TBind(x, x)
    result = ty.specialize_top(t1)
    assert isinstance(result, TVar.TVar) and result != x != y


def test_specialize_xxy(atoms):
    x, y, b, n = atoms
    t1 = TBind.TBind(x, TOp.TOp('->', [x, y]))
    result = ty.specialize_top(t1)
    assert isinstance(result, TOp.TOp) and \
        ty.is_function(result) and \
        (result.args[0] != x != y) and \
        result.args[1] == y


def test_specialize_xxb(atoms):
    x, y, b, n = atoms
    t1 = TBind.TBind(x, TOp.TOp('->', [x, b]))
    result = ty.specialize_top(t1)
    assert isinstance(result, TOp.TOp) and \
        ty.is_function(result) and \
        (result.args[0] != x != y) and \
        result.args[1] == b


def test_substitute_x_b(atoms):
    x, y, b, n = atoms
    assert ty.substitute(x, {x: b}) == b


def test_substitute_xx_b(atoms):
    x, y, b, n = atoms
    t1 = TOp.TOp('->', [x, x])
    t2 = TOp.TOp('->', [b, b])
    assert ty.substitute(t1, {x: b}) == t2


def test_substitute_xxx_b(atoms):
    x, y, b, n = atoms
    t = TBind.TBind(x, TOp.TOp('->', [x, x]))
    assert ty.substitute(t, {x: b}) == t


def test_substitute_xxy_b(atoms):
    x, y, b, n = atoms
    t1 = TBind.TBind(x, TOp.TOp('->', [x, y]))
    t2 = TBind.TBind(x, TOp.TOp('->', [x, b]))
    assert ty.substitute(t1, {y: b}) == t2


def test_update_x(atoms):
    x, y, b, n = atoms
    env = {}
    t1 = ty.update(x, env, {})
    assert isinstance(t1, TBind.TBind) and \
        t1.variable == x and t1.body == x


def test_update_x__xy(atoms):
    x, y, b, n = atoms
    env = {}
    t1 = ty.update(x, env, {x: y})
    assert isinstance(t1, TBind.TBind) and \
        t1.variable == y and t1.body == y


def test_update_x_zx_xy(atoms):
    x, y, b, n = atoms
    z = Var.Var('z')
    env = {z: x}
    sub = {x: y}
    t1 = ty.update(x, env, sub)
    assert t1 == ty.substitute(x, sub)


def test_update_b_zx_xy(atoms):
    x, y, b, n = atoms
    z = Var.Var('z')
    env = {z: b}
    t1 = ty.update(b, env, {x: y})
    assert t1 == b


def test_free_vars_x(atoms):
    x, y, b, n = atoms
    assert ty.free_vars(x) == {x}


def test_free_vars_b(atoms):
    x, y, b, n = atoms
    assert ty.free_vars(b) == set()


def test_free_vars_xy(atoms):
    x, y, b, n = atoms
    assert ty.free_vars(TOp.TOp('->', [x, y])) == {x, y}


def test_free_vars_xxy(atoms):
    x, y, b, n = atoms
    assert ty.free_vars(TBind.TBind(x, TOp.TOp('->', [x, y]))) == {y}


def test_alpha_xxx_yyy(atoms):
    x, y, b, n = atoms
    assert ty.alpha(TBind.TBind(x, TOp.TOp('->', [x, x])),
                    TBind.TBind(y, TOp.TOp('->', [y, y]))) == {x: y}


def test_alpha_xxx_yxy(atoms):
    x, y, b, n = atoms
    assert ty.alpha(TBind.TBind(x, TOp.TOp('->', [x, x])),
                    TBind.TBind(y, TOp.TOp('->', [x, y]))) is None


def test_alpha_xx_yy(atoms):
    x, y, b, n = atoms
    assert ty.alpha(TOp.TOp('->', [x, x]),
                    TOp.TOp('->', [y, y])) is None


def test_alpha_xbb_ynn(atoms):
    x, y, b, n = atoms
    assert ty.alpha(TBind.TBind(x, TOp.TOp('->', [b, b])),
                    TBind.TBind(y, TOp.TOp('->', [n, n]))) is None


def test_alpha_xxb_yyb(atoms):
    x, y, b, n = atoms
    assert ty.alpha(TBind.TBind(x, TOp.TOp('->', [x, b])),
                    TBind.TBind(y, TOp.TOp('->', [y, b]))) == {x: y}


def test_alpha_natlist_natlist(atoms):
    x, y, b, n = atoms
    natlist = TOp.TOp('LIST', [TOp.TOp('NAT', [])])
    nl2nl = TOp.TOp('->', [natlist, natlist])
    assert ty.alpha(nl2nl, nl2nl) == {}
