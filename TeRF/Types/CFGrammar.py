import copy
import itertools
import numpy as np
from scipy import stats
from scipy import misc as smisc
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A
import TeRF.Types.Grammar as Grammar
import TeRF.Types.Rule as R
import TeRF.Types.Trace as T
import TeRF.Types.Variable as V


class CFG(Grammar.Grammar):
    def __init__(self, rules=None, **kwargs):
        super(CFG, self).__init__(rules=rules, **kwargs)

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
        print 'p_n_rules', p_n_rules
        p_rules = sum(rule.log_p(self) for rule in grammar)
        print 'p_rules', p_rules
        return p_n_rules + p_rules

    def log_p_rule(self, rule, start=None):
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
        # get the parses for the lhs
        with Grammar.scope(self, reset=True):
            parse_ps = []
            lhs_parses = self.parse(rule.lhs, start=start)
            for lhs_parse in lhs_parses:
                rhs_ps = []
                for rhs in rule.rhs:
                    with Grammar.scope(self, scope=lhs_parse[2], lock=True):
                        rhs_ps.append(rhs.log_p(self, start=start))
                parse_ps.append(len(rule.rhs)*lhs_parse[0] + sum(rhs_ps))
        return smisc.logsumexp(parse_ps) if parse_ps != [] else -np.inf

    def sample_rule(self, start=None):
        """
        sample a Rule from the grammar
        
        Returns
        -------
        TeRF.Types.Rule
            the sampled rule
        """
        lhs = None
        while not isinstance(lhs, A.Application):
            with Grammar.scope(self):
                lhs = self.sample_term(start=start)
                print 'lhs', lhs.to_string()
        with Grammar.scope(self, lock=True):
            rhs = self.sample_term(start=start)
            print 'rhs', rhs.to_string()
        return R.Rule(lhs, rhs)

    def log_p_term(self, term, start=None):
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
            parses = self.parse(term, start=start)
            return smisc.logsumexp(list(zip(*parses)[0]))
        except IndexError:
            return misc.log(0.0)

    def sample_term(self, start=None, max_steps=50):
        """
        sample a term from the grammar

        Returns
        -------
        TeRF.Types.Term
            the sampled term
        """
        start = self.start if start is None else start
        # TODO: does the grammar terminate? How do you respond if not?
        trace = T.Trace(self, start, type='one', max_steps=max_steps)
        return trace.rewrite(states=['normal'])

    def sample_term_t(self, term, max_steps=50):
        # pick a subterm
        print 'term:', term.to_string()
        term = copy.deepcopy(term)
        places = list(term.places)
        print 'places:', places
        while places != []:
            place_idx = np.random.choice(len(places))
            place = places[place_idx]
            print 'place:', place
            subterm = term.place(place)
            print 'subterm:', subterm.to_string()

            # find a non-terminal that could have generated it
            parses = [p for p in self.get_possible_parses(subterm)
                      if p[1] in self]
            if parses == []:
                places.remove(place)
                continue
            for p in parses:
                pterm = term.replace(place, p[1])
                print 'pterm', pterm
                parses = self.parse(pterm)
                print 'parses'
                print parses
                if parses == []:
                    parses.remove(p)
            parse_ps = misc.renormalize([p[0] for p in parses])
            i = np.random.choice(len(parses), p=parse_ps)
            parse = parses[i]
            print 'parse:', parse
            
            # compute the scope for the subtree
            scope = self.scope.copy()
            for p in term.places:
                if p == place:
                    break
                term_at_p = term.place(p)
                if isinstance(term_at_p, V.Var) and \
                   term_at_p not in scope.scope and \
                   term_at_p in parse[2].scope:
                    scope[term_at_p] = parse[2].scope[term_at_p]

            # generate the tree and substitute it into the new term
            with Grammar.scope(self, scope=scope):
                new_subterm = self.sample_term(start=parse[1],
                                               max_steps=max_steps)
                print 'new_subterm:', new_subterm.to_string()
                term = term.replace(place, new_subterm)
            print 'returning:', term
            return term
        raise ValueError('sample_term_t: term cannot be resampled')

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
        parses = [parse for parse in self.get_possible_parses(term)
                  if start.unify(parse[1], 'alpha') is not None]
        return parses

    def get_possible_parses(self, term):
        if isinstance(term, V.Var):
            # is it in the scope already
            try:
                nonterminal = self.scope.scope[term]
                n_options = len(self[nonterminal]) + \
                    len(self.scope.find(nonterminal)) + \
                    int(not self.scope.locked)
                log_p = -misc.log(n_options)
                parses = [(log_p, nonterminal, self.scope.copy())]
            # nope, so assume we added it
            except KeyError:
                parses = []
                if not self.scope.locked:
                    for rule in self:
                        nonterminal = rule.lhs
                        n_options = len(self[nonterminal]) + \
                            len(self.scope.find(nonterminal)) + \
                            int(not self.scope.locked)
                        log_p = -misc.log(n_options)
                        new_scope = self.scope.copy()
                        new_scope.scope[term] = nonterminal
                        parses.append((log_p, nonterminal, new_scope))
        else:
            if term.head.arity == 0:
                parses = [(0.0, term, self.scope.copy())]
            else:
                subparses = []
                scopes = [self.scope.copy()]
                for branch in term.body:
                    tmp_scopes = []
                    tmp_results = []
                    for scope in scopes:
                        with Grammar.scope(self, scope=scope):
                            results = self.get_possible_parses(branch)
                            tmp_results += results
                            tmp_scopes += list(zip(*results)[2])
                    scopes = list(set(tmp_scopes))
                    subparses.append(tmp_results)
                parses = []
                for body in itertools.product(*subparses):
                    log_ps, term_body, parse_scopes = zip(*body)
                    if all(parse_scopes[-1].entails(ps)
                           for ps in parse_scopes[:-1]):
                        log_p = sum(log_ps)
                        term = A.App(term.head, list(term_body))
                        scope = body[-1][2]
                        parses.append((log_p, term, scope))
        for parse in parses:
            for rule in self:
                for clause in rule:
                    if parse[1] == clause.rhs0:
                        parses.append((parse[0] -
                                       misc.log(len(rule.rhs) +
                                                len(self.scope.find(rule.lhs)) +
                                                int(not self.scope.locked)),
                                       clause.lhs, parse[2]))
        return parses


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

    print '\nPossible Parses for {}:\n'.format(term.to_string())
    print_parses(cfg.get_possible_parses(term))

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
