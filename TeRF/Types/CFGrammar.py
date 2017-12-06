import numpy as np
from scipy import stats
import TeRF.Types.Application as A
import TeRF.Types.Grammar as Grammar
import TeRF.Types.Rule as R
import TeRF.Types.Trace as T


class CFG(Grammar.Grammar):
    def __init__(self, rules=None, **kwargs):
        super(CFG, self).__init__(rules=rules, **kwargs)
        if rules is not None:
            self.update(rules)

    def __setitem__(self, index, value):
        if value.lhs.head.arity != 0:
            err_str = '__setitem__: context-sensitive rule -> {}'
            raise ValueError(err_str.format(value))
        Grammar.Grammar.__setitem__(self, index, value)

    def n_options(self, term):
        try:
            return ((len(self[term]) +
                     int(not self.scope.locked) +
                     len(self.scope.find(term))))
        except KeyError:
            return 0


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
    """

    def sample_grammar(self, p_rule=0.5, start=None, **kwargs):
        """
        sample a grammar from the grammar

        Returns
        -------
        TeRF.Types.Grammar
            the sampled grammar
        """
        n_rules = stats.geom.rvs(p=p_rule)-1
        rules = [self.sample_rule(start=start) for _ in xrange(n_rules)]
        return Grammar.Grammar(rules, **kwargs)

    def sample_rule(self, start=None):
        """
        sample a rule from the grammar

        Returns
        -------
        TeRF.Types.Rule
            the sampled rule
        """
        lhs = None
        while not isinstance(lhs, A.Application):
            with Grammar.scope(self):
                lhs = self.sample_term(start=start)
                with Grammar.scope(self, lock=True):
                    rhs = self.sample_term(start=start)
        return R.Rule(lhs, rhs)

    def sample_term(self, start=None, max_steps=50):
        """
        sample a term from the grammar

        TODO
        ----
        - What if the grammar doesn't terminate? Is there a better solution
          than a hard limit?

        Returns
        -------
        TeRF.Types.Term
            the sampled term
        """
        start = self.start if start is None else start
        trace = T.Trace(self, start, type='one', max_steps=max_steps)
        return trace.rewrite(states=['normal'])


class FPCFG(FCFG, PCFG):
    pass


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg

    def print_parses(ps):
        for p in ps:
            print_parse(p)

    def print_parse(p):
        print '({:.1f}, {}, {}'.format(1./np.exp(p[0]), p[1].to_string(), p[2])

    cfg = tg.head_pcfg

    print '\nCFG:\n', cfg

    term = tg.head_lhs

    print '\nFull Parse for {}:\n'.format(term.to_string())
    print_parses(cfg.parse(term))

    print '\nLog Probability for {}:\n'.format(term.to_string())
    log_p = cfg.log_p_term(term)
    print log_p, 1./np.exp(log_p)

    rule = tg.head_rule

    print '\nLog Probability for {}:\n'.format(rule)
    log_p = cfg.log_p_rule(rule)
    print log_p, 1./np.exp(log_p)

    g = tg.head_g

    print '\nLog Probability for a grammar:\n'.format(rule)
    log_p = cfg.log_p_grammar(g, 0.5)
    print log_p, 1./np.exp(log_p)

    print
    for _ in xrange(20):
        with Grammar.scope(cfg):
            # term = cfg.start.single_rewrite(cfg, 'all', 'eager')
            term = cfg.sample_term()
            print term.to_string()

    print
    for _ in xrange(20):
        with Grammar.scope(cfg, lock=True, reset=True):
            # term = cfg.start.single_rewrite(cfg, 'all', 'eager')
            term = cfg.sample_term()
            print term.to_string()
