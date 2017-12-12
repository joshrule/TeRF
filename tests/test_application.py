import copy
import pytest


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
    x = Variable.Variable('x')

    return dot, A, B, x


@pytest.fixture(scope="module")
def objs():
    import TeRF.Types.Atom as Atom
    import TeRF.Types.Operator as Operator
    import TeRF.Types.Application as Application
    import TeRF.Types.Variable as Variable
    reload(Atom)
    reload(Operator)
    reload(Application)
    reload(Variable)

    dot = Operator.Operator('.', 2)
    A = Operator.Operator('A')
    B = Operator.Operator('B')
    x = Variable.Variable('x')

    a = Application.Application(A, [])
    b = Application.Application(dot,
                                [Application.Application(A, []),
                                 Application.Application(B, [])])
    c = Application.Application(dot,
                                [x,
                                 Application.Application(B, [])])
    return a, b, c


def test_application_repr_a(objs):
    a, b, c = objs
    assert repr(a) == ('Application(' +
                       'head=Operator(name=\'A\', arity=0, identity=1), ' +
                       'args=[])')


def test_application_repr_b(objs):
    a, b, c = objs
    rep_a = ('Application(' +
             'head=Operator(name=\'A\', arity=0, identity=1), ' +
             'args=[])')
    rep_b = ('Application(' +
             'head=Operator(name=\'B\', arity=0, identity=2), ' +
             'args=[])')
    assert repr(b) == ('Application(' +
                       'head=Operator(name=\'.\', arity=2, identity=0), ' +
                       'args=[' + rep_a + ', ' + rep_b + '])')


def test_application_repr_c(objs):
    a, b, c = objs
    rep_x = 'Variable(name=\'x\', identity=3)'
    rep_b = ('Application(' +
             'head=Operator(name=\'B\', arity=0, identity=2), ' +
             'args=[])')
    assert repr(c) == ('Application(' +
                       'head=Operator(name=\'.\', arity=2, identity=0), ' +
                       'args=[' + rep_x + ', ' + rep_b + '])')


def test_application_str_a(objs):
    a, b, c = objs
    assert str(a) == 'A[]'


def test_application_str_b(objs):
    a, b, c = objs
    assert str(b) == '.[A[], B[]]'


def test_application_str_c(objs):
    a, b, c = objs
    assert str(c) == '.[x_, B[]]'


def test_application_a_eq_a(objs):
    a, b, c = objs
    assert (a == a) is True


def test_application_a_eq_copy_a(objs):
    a, b, c = objs
    assert (a == copy.copy(a)) is True


def test_application_a_eq_deepcopy_a(objs):
    a, b, c = objs
    assert (a == copy.deepcopy(a)) is True


def test_application_a_eq_b(objs):
    a, b, c = objs
    assert (a == b) is False


def test_application_a_eq_c(objs):
    a, b, c = objs
    assert (a == c) is False


def test_application_b_eq_c(objs):
    a, b, c = objs
    assert (b == c) is False


def test_application_hash_a(atoms, objs):
    dot, A, B, x = atoms
    a, b, c = objs
    assert hash(a) == hash((A, ()))


def test_application_hash_c(atoms, objs):
    import TeRF.Types.Application as Application
    dot, A, B, x = atoms
    a, b, c = objs
    assert hash(c) == hash((dot, (x, Application.Application(B, []))))


def test_application_a_ne_a(objs):
    a, b, c = objs
    assert (a != a) is False


def test_application_a_ne_b(objs):
    a, b, c = objs
    assert (a != b) is True


def test_application_a_ne_c(objs):
    a, b, c = objs
    assert (a != c) is True


def test_application_len_a(objs):
    a, b, c = objs
    assert len(a) == 1


def test_application_len_b(objs):
    a, b, c = objs
    assert len(b) == 3


def test_application_len_c(objs):
    a, b, c = objs
    assert len(c) == 3
