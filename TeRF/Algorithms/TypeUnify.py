import TeRF.Types.TypeOperator as TOp
import TeRF.Types.TypeBinding as TBind
import TeRF.Types.TypeVariable as TVar
import TeRF.Algorithms.TypeUtils as ty


def uf_unify(equations, kind='unification'):
    sets = union_find()
    prompts = []
    for t1, t2 in equations:
        sets.make_set(t1)
        sets.make_set(t2)
        prompts.append(t1)
    while len(equations) != 0:
        x, y = equations.pop()
        u, v = sets.find(x), sets.find(y)
        if (u == v):
            continue
        elif isinstance(u, TVar.TVar):
            sets.union(v, u)
        elif isinstance(v, TVar.TVar) and kind != 'match':
            sets.union(u, v)
        elif u.head == v.head:
            equations |= set(zip(u.args, v.args))
        else:
            return None
    solution = sets.make_mapping(prompts, {})
    return solution


def tapl_unify(cs, kind='unification'):
    """unify a set of constraints - recursively"""
    try:
        (s, t) = cs.pop()
    except KeyError:
        return {}

    if s == t:
        return unify(cs, kind=kind)
    elif isinstance(s, TVar.TVar) and s not in free_vars(t):
        partial = unify(substitute(cs, {s: t}), kind=kind)
        return compose(partial, {s: t})
    elif (isinstance(t, TVar.TVar) and
          t not in free_vars(s) and
          kind != 'match'):
        partial = unify(substitute(cs, {t: s}), kind=kind)
        return compose(partial, {t: s})
    elif (isinstance(s, TOp.TOp) and
          isinstance(t, TOp.TOp) and
          s.head == t.head):
        arg_cs = {(st, tt) for st, tt in zip(s.args, t.args)}
        return unify(cs | arg_cs, kind=kind)
    return None


def unify(cs, kind='unification'):
    """unify a set of constraints - iteratively"""
    cs = list(cs)
    sub = {}
    stack = []
    while True:
        try:
            (s, t) = cs.pop()
            if s == t:
                continue
        except IndexError:
            while True:
                try:
                    sub = compose(sub, stack.pop())
                except IndexError:
                    break
            return sub

        try:
            if s.head == t.head:
                cs += zip(s.args, t.args)
                continue
        except AttributeError:
            pass

        if isinstance(s, TVar.TVar) and s not in free_vars(t):
            cs = [(fast_sub(x, s, t), fast_sub(y, s, t))
                  for x, y in cs]
            stack.append({s: t})
        elif (isinstance(t, TVar.TVar) and t not in free_vars(s) and
              kind != 'match'):
            cs = [(fast_sub(x, t, s), fast_sub(y, t, s))
                  for x, y in cs]
            stack.append({t: s})
        else:
            return None


def fast_sub(the_type, k, v):
    if isinstance(the_type, TOp.TOp):
        return TOp.TOp(the_type.head,
                       [fast_sub(arg, k, v) for arg in the_type.args])
    return v if the_type == k else the_type


def free_vars(type, env=None):
    """compute the free variables in a term"""
    if isinstance(type, TVar.TVar):
        return {type} if env is None or type not in env.values() else set()
    elif isinstance(type, TOp.TOp):
        return {var for arg in type.args for var in free_vars(arg, env=env)}
    elif isinstance(type, TBind.TBind):
        return free_vars(type.body, env=env).difference({type.variable})
    raise TypeError('not a type: {!r}'.format(type))


def compose(sub1, sub2):
    """compose two substitutions"""
    try:
        sub1.update({k: ty.substitute(v, sub1) for k, v in sub2.iteritems()})
        return sub1
    except AttributeError:
        raise TypeError('invalid substitution')


def substitute(cs, sub):
    """substitution for a set of pairs"""
    return {(ty.substitute(s, sub), ty.substitute(t, sub)) for s, t in cs}


class UnionFind(object):
    """src: code.activestate.com/recipes/215912-union-find-data-structure"""
    def __init__(self):
        self.num_weights = {}
        self.parent_pointers = {}
        self.num_to_xs = {}
        self.xs_to_num = {}

    def make_set(self, x):
        self.find(x)

    def find(self, x):
        if x not in self.xs_to_num:
            obj_num = len(self.xs_to_num)
            self.num_weights[obj_num] = 1
            self.xs_to_num[x] = obj_num
            self.num_to_xs[obj_num] = x
            self.parent_pointers[obj_num] = obj_num
            return x
        stk = [self.xs_to_num[x]]
        par = self.parent_pointers[stk[-1]]
        while par != stk[-1]:
            stk.append(par)
            par = self.parent_pointers[par]
        for i in stk:
            self.parent_pointers[i] = par
        return self.num_to_xs[par]

    def union(self, x1, x2):
        o1p = self.find(x1)
        o2p = self.find(x2)
        if o1p != o2p:
            on1 = self.xs_to_num[o1p]
            on2 = self.xs_to_num[o2p]
            w1 = self.num_weights[on1]
            w2 = self.num_weights[on2]
            if w1 < w2:
                o1p, o2p, on1, on2, w1, w2 = o2p, o1p, on2, on1, w2, w1
            self.num_weights[on1] = w1+w2
            del self.num_weights[on2]
            self.parent_pointers[on2] = on1


class union_find(object):
    def __init__(self):
        self.items = {}

    def make_set(self, x):
        self.find(x)

    def find(self, x):
        # make a node if necessary
        if x not in self.items:
            self.items[x] = uf_node(x)
            return x

        # perform path compression
        stk = [self.items[x]]
        par = self.items[stk[-1].item].parent
        while par != stk[-1]:
            stk.append(par)
            par = self.items[par.item]
        for i in stk:
            i.parent = par
        return self.items[x].parent.item

    def union(self, x, y):
        x_root = self.find(x)
        y_root = self.find(y)
        if x_root != y_root:
            x_root_item = self.items[x_root]
            y_root_item = self.items[y_root]
            if x_root_item.rank < y_root_item.rank:
                x_root_item.parent = y_root_item
            elif x_root_item.rank > y_root_item.rank:
                y_root_item.parent = x_root_item
            else:
                y_root_item.parent = x_root_item
                x_root_item.rank += 1

    def make_mapping(self, xs, sub):
        for x in xs:
            x_prime = self.functional(self.find(x))
            if self.items[x_prime].acyclic:
                return sub
            if self.items[x_prime].visited:
                return None
            try:
                self.items[x_prime].visited = True
                for arg in x_prime.args:
                    sub = self.make_mapping([arg], sub)
                self.items[x_prime].visited = False
            except AttributeError:
                pass
            self.items[x_prime].acyclic = True
            for v in self.variables(self.find(x_prime)):
                if v != x_prime:
                    sub[v] = x_prime
        return sub

    def variables(self, x):
        x_parent = self.items[x].parent
        return {item
                for item, node in self.items.iteritems()
                if x_parent == node.parent and isinstance(item, TVar.TVar)}

    def functional(self, x):
        x_parent = self.items[x].parent
        for item, node in self.items.iteritems():
            if x_parent == node.parent and isinstance(item, TOp.TOp):
                return item
        return x


class uf_node(object):
    def __init__(self, x):
        self.item = x
        self.parent = self
        self.rank = 0
        self.visited = False
        self.acyclic = False
