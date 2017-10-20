import TeRF.Types.Grammar as G


class LOT(object):
    """
    a Language Of Thought (LOT; Fodor, 1975)

    LOTs are a collection of three distinct grammars. Each plays a different
    role in thought:
    1. The primitive grammar is flat, and denotes *what basic concepts exists*.
    2. The syntax grammar is context-free and denotes *how concepts combine*.
    3. The semantics grammar denotes *how concepts behave*.

    Notes
    -----
    - These three grammars could be combined into a single grammar with more
      sophisticated reasoning and inference algorithms over the unified grammar

    Parameters
    ----------
    primitives : Grammar.FlatCFG or set of Operator
        (default: None)
        the LOT's primitives. If None, search `syntax` and `semantics` to seed.
    syntax : Grammar.CFG (default: None)
        the LOT's syntax. If None, default to the primitive grammar
    semantics : Grammar.Grammar (default: None)
        the LOT's semantics. If None, default to an empty grammar.
    """
    def __init__(self, primitives=None, syntax=None, semantics=None):
        if primitives is None:
            primitives = set() if semantics is None else semantics.operators
            primitives |= set() if syntax is None else syntax.operators
        if isinstance(primitives, G.FlatCFG):
            self.primitives = primitives
        else:
            self.primitives = G.FlatCFG(primitives)

        # now that we have our primitives, we check the syntax
        if syntax is None:
            syntax = G.CFG([rule for rule in self.primitives])
        # TODO: can terms in `syntax` be parsed by `primitives`?
        if isinstance(syntax, G.CFG):
            self.syntax = syntax
        else:
            raise ValueError('LOT: syntax must be a CFG')

        # now that we have our primitives and syntax, check our semantics
        if semantics is None:
            syntax = G.Grammar()
        # TODO: can terms in `semantics` be parsed by `syntax`?
        if isinstance(semantics, G.Grammar):
            self.semantics = semantics
        else:
            raise ValueError('LOT: semantics must be a Grammar')

    def __str__(self):
        return '\n\n'.join([str(self.primitives),
                            str(self.syntax),
                            str(self.semantics)])


if __name__ == '__main__':
    import TeRF.Types.Application as A
    import TeRF.Types.Operator as O
    import TeRF.Types.Rule as R
    import TeRF.Types.Variable as V

    def f(x, xs=None):
        if xs is None:
            xs = []
        return A.App(x, xs)

    # test Grammar
    S = O.Operator('S', 0)
    K = O.Operator('K', 0)
    x = V.Variable('x')
    y = V.Variable('y')
    z = V.Variable('z')
    a = O.Operator('.', 2)

    lhs_s = f(a, [f(a, [f(a, [f(S), x]), y]), z])
    rhs_s = f(a, [f(a, [x, z]), f(a, [y, z])])
    lhs_k = f(a, [f(a, [f(K), x]), y])
    rhs_k = x

    rule_s = R.Rule(lhs_s, rhs_s)
    rule_k = R.Rule(lhs_k, rhs_k)

    g = G.Grammar(rules={rule_s, rule_k})

    # test CFG
    start = O.Operator('START', 0)
    T = O.Operator('T', 0)
    lhs_start = f(start)
    rhs_start = {f(S), f(K)}
    lhs_k = f(K)
    rhs_k = f(a, [f(S), f(a, [f(K), f(S)])])
    lhs_s = f(S)
    rhs_s = {f(T), f(K)}

    rule_start = R.Rule(lhs_start, rhs_start)
    rule_s = R.Rule(lhs_s, rhs_s)
    rule_k = R.Rule(lhs_k, rhs_k)

    cfg = G.CFG(rules={rule_start, rule_s, rule_k}, start=start)

    # test FlatCFG
    flat_cfg = G.FlatCFG({T, K, S, a}, start=start)

    lot = LOT(primitives=flat_cfg, syntax=cfg, semantics=g)

    print lot
