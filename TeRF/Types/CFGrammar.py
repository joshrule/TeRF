import itertools
from scipy import stats
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A
import TeRF.Types.Grammar as Grammar
import TeRF.Types.Rule as R
import TeRF.Types.Variable as V


class CFG(Grammar.Grammar):
    def __init__(self, rules=None, start=None):
        super(CFG, self).__init__(rules=rules, start=start)

        if rules is not None:
            for rule in rules:
                if rule.lhs.head.arity != 0:
                    err_str = 'CFG: context-sensitive rule -> {}'
                    raise ValueError(err_str.format(rule))

    def __setitem__(self, index, value):
        if value.lhs.head.arity != 0:
            err_str = '__setitem__: context-sensitive rule -> {}'
            raise ValueError(err_str.format(value))
        Grammar.Grammar.__setitem__(self, index, value)


class FCFG(CFG):
    def __init__(self, primitives, **kwargs):
        super(FCFG, self).__init__(**kwargs)
        primitives -= {self.start.head}
        rules = [R.Rule(self.start, {A.App(p, [self.start]*p.arity)
                                     for p in primitives})]
        self.update(rules)

    def __setitem__(self, index, value):
        if value.lhs != self.start:
            raise ValueError('__setitem__: FCFGs can only have one rule')
        Grammar.Grammar.__setitem__(self, 0, value)


class PCFG(CFG):
    """
    A limited PCFG -- the distributions over weights are fixed.

    TODO
    ----
    - add weights to the grammar
    - handle variables in PCFG.get_possible_parses
    """
    def log_p_grammar(self, grammar, p_rule):
        """
        compute the log prior probability of a grammar

        Parameters
        ----------
        grammar: TeRF.Types.Grammar
            the grammar whose probability we're computing
        p_rule: float
            the probability of adding another rule

        Returns
        -------
        float
            log(p(grammar | self, p_rule))
        """
        p_n_rules = stats.geom.logpmf(len(grammar.clauses)+1, p=p_rule)
        p_rules = sum(rule.log_p(self) for rule in grammar)
        return p_n_rules + p_rules

    def log_p_rule(self, rule):
        """
        give the log prior probability of a TeRF.Types.Rule

        Parameters
        ----------
        rule : TeRF.Types.Rule
            the rule whose probability is being computed

        Returns
        -------
        float
            log(p(rule | self))
        """
        with Grammar.scope(self, 'clear'):
            p_lhs = rule.lhs.log_p(self) * len(rule.rhs)
            with Grammar.scope(self, 'close'):
                p_rhs = sum(rhs.log_p(self) for rhs in rule.rhs)
        return p_lhs + p_rhs

    def log_p_term(self, term):
        """
        give the log prior probability of a TeRF.Types.Term

        Parameters
        ----------
        term : TeRF.Types.Term
            the term whose log prior probability we're computing

        Returns
        -------
        float
            log(p(term | self))
        """
        try:
            return sum(zip(*self.parse(term))[0])
        except IndexError:
            return misc.log(0.0)

    def parse(self, term, start=None):
        """
        parse a term

        Parameters
        ----------
        term : TeRF.Types.Term
            the term being parsed

        Returns
        -------
        list of (float, TeRF.Types.Term) tuples
            the possible parses and their log probabilities
        """
        start = self.start if start is None else start
        return [parse for parse in self.get_possible_parses(term)
                if start.unify(parse[1], 'alpha') is not None]

    def get_possible_parses(self, term):
        if isinstance(term, V.Var):
            raise ValueError('get_possible_parses: no variables in PCFGs')
        if term.head.arity == 0:
            parses = [(0.0, term)]
        else:
            subparses = [self.get_possible_parses(branch)
                         for branch in term.body]
            parses = []
            for body in itertools.product(*subparses):
                term = A.App(term.head, list(zip(*body)[1]))
                log_p = sum(zip(*body)[0])
                parses.append((log_p, term))
        for parse in parses:
            for rule in self:
                for clause in rule:
                    if parse[1] == clause.rhs0:
                        parses.append((parse[0] - misc.log(len(rule.rhs)),
                                       clause.lhs))
        return parses


class FPCFG(FCFG, PCFG):
    pass


if __name__ == '__main__':
    import TeRF.Types.Operator as Op

    def f(x, xs=None):
        if xs is None:
            xs = []
        return A.App(x, xs)

    def g(x, y):
        return A.App(a, [x, y])

    # test Grammar
    s = Op.Operator('START', 0)
    xs = Op.Operator('list', 0)
    num = Op.Operator('number', 0)
    nil = Op.Operator('nil', 0)
    nel = Op.Operator('nel', 0)
    cons = Op.Operator('cons', 0)
    zero = Op.Operator('0', 0)
    one = Op.Operator('1', 0)
    two = Op.Operator('2', 0)
    three = Op.Operator('3', 0)
    a = Op.Operator('.', 2)

    rule_s = R.Rule(f(s), f(xs))
    rule_xs = R.Rule(f(xs), {f(nil), f(nel)})
    rule_nel = R.Rule(f(nel), g(g(f(cons), f(num)), f(xs)))
    rule_num = R.Rule(f(num), {f(zero), f(one), f(two), f(three)})

    # test CFG
    cfg = PCFG(rules={rule_s, rule_xs, rule_nel, rule_num}, start=f(s))

    print '\nCFG:\n', cfg

    term = f(three)
    parses = cfg.get_possible_parses(term)

    print '\nPossible Parses for {}:\n'.format(term.to_string())
    for parse in parses:
        print parse

    term = g(g(f(cons), f(three)), f(nil))
    parses = cfg.get_possible_parses(term)

    print '\nPossible Parses for {}:\n'.format(term.to_string())
    for parse in parses:
        print parse

    print '\nFull Parse for {}:\n'.format(term.to_string())
    print cfg.parse(term)

    print '\nLog Probability for {}:\n'.format(term.to_string())
    print cfg.log_p_term(term)

    rule = R.Rule(term, g(g(f(cons), f(two)), f(nil)))

    print '\nLog Probability for {}:\n'.format(rule)
    print cfg.log_p_rule(rule)

    rule1 = R.Rule(g(g(f(cons), f(three)), f(nil)),
                   g(g(f(cons), f(two)), f(nil)))
    rule2 = R.Rule(g(g(f(cons), f(one)), f(nil)),
                   g(g(f(cons), f(zero)), f(nil)))
    rule3 = R.Rule(g(g(f(cons), f(one)), f(nil)),
                   g(g(f(cons), f(three)), f(nil)))

    g = Grammar.Grammar(rules={rule1, rule2, rule3})

    print '\nLog Probability for a grammar:\n'.format(rule)
    print cfg.log_p_grammar(g, 0.5)

    # test FlatCFG
    flat_cfg = FCFG({one, two, three, a})

    print '\nFlat CFG:\n', flat_cfg
