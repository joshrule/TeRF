import itertools as ittl
import numpy as np
import scipy.misc as sm
import scipy.stats as ss
import TeRF.Miscellaneous as tmisc
import TeRF.Types.Application as A
import TeRF.Types.Rule as R
import TeRF.Types.Variable as V
import TeRF.Types.TRS as TRS


class (object):
    """
    Sample atoms, terms, rules, and TRSs using fixed production probabilities.

    Sampling breaks down into a Context Free portion, in which we are concerned
    only with operators, and a context-sensitive portion, in which we are
    concerned with variables.

    Parameters
    ----------
    signature : TeRF.Types.Signature
        a collection of operators for sampling applicative terms
    variables : set of TeRF.Types.Variable
        a collection of variables for sampling variable terms.
    probs : a dictionary of TeRF.Types.Operator keys and float values
        the production probabilities
    """
    def __init__(self, signature, variables=None, probs=None):
        self.signature = signature
        self.variables = set() if variables is None else set(variables)
        if probs is None:
            self.probs = {op: 1./(len(signature)+1) for op in signature}
            self.probs['var'] = 1./(len(signature) + 1)
        else:
            self.probs = probs

    def sample_atom(self, invent=True):
        """
        sample an atom

        Parameters
        ----------
        invent : bool
            can invent new variables if True, else no new variables are allowed
            (optional: True)

        Returns
        -------
        head : TeRF.Types.Atom
            either an operator or a variable
        """
        if not (self.signature.terminals or self.variables or invent):
            raise ValueError('sample_head: no terminals!')

        # sample from the PCFG (only add variable option if available)
        options = (list(self.signature._elements) +
                   (['var'] if (invent or self.variables) else []))
        ps = [self.probs[o] for o in options]
        ps = [p/float(sum(ps)) for p in ps]
        atom = np.random.choice(options, p=ps)

        # If you chose 'var', sample a variable
        if atom == 'var':
            options = list(self.variables) + ([V.Var()] if invent else [])
            atom = np.random.choice(options)
            self.variables.add(atom)

        return atom

    def log_p_atom(self, atom, invent=True):
        """
        give the log-probability of sampling a particular atom

        Parameters
        ----------
        atom : TeRF.Types.Atom
            the atom whose probability is being computed
        invent : bool
            can invent new variables if True, else no new variables are allowed
            (optional: True)

        Returns
        -------
        float
            the log prior probability of `atom`
        """
        if atom in self.signature:
            return tmisc.log(self.probs[atom])
        if invent and isinstance(atom, V.Var):
            return tmisc.log(self.probs['var']) - \
                tmisc.logNof(list(self.variables) + ['var'])
        if atom in self.variables:
            return tmisc.log(self.probs['var']) - \
                tmisc.logNof(list(self.variables))
        return tmisc.log(0)

    def sample_term(self, invent=True):
        """
        sample a TeRF.Types.Term from the grammar

        Parameters
        ----------
        invent : bool
            can invent new variables if True else no new variables are allowed
            (optional: True)

        Returns
        -------
        TeRF.Types.Term
            a term sampled from the prior
        """
        head = self.sample_atom(invent=invent)
        try:
            body = [self.sample_term(invent=invent)
                    for _ in ittl.repeat(None, head.arity)]
            return A.App(head, body)
        except AttributeError:
            if invent:
                self.variables.add(head)
            return head

    def log_p(self, term, invent=True):
        """
        give the log prior probability of a TeRF.Types.Term

        Parameters
        ----------
        term : TeRF.Types.Term
            the term whose log prior probability we're computing
        invent : bool
            can invent new variables if True else no new variables are allowed
            (optional: True)

        Returns
        -------
        p : float
            the log prior probability of `term`
        """
        p = self.log_p_atom(term.head, invent)
        try:
            for t in term.body:
                p += self.log_p(t, invent)
        except AttributeError:
            if invent:
                self.variables.add(term)
        return p

    def sample_rule(self, invent=True):
        """
        sample a TeRF.Types.Rule

        Parameters
        ----------
        invent : bool (default: True)
            can invent new variables if True else no new variables are allowed

        Returns
        -------
        TeRF.Types.Rule
            the sampled rule
        """
        lhs = None
        vars = self.variables.copy()
        while not isinstance(lhs, A.Application):
            self.variables = vars.copy()
            lhs = self.sample_term(invent)
        self.variables = set(lhs.variables)
        rhs = self.sample_term(invent=False)
        return R.Rule(lhs, rhs)

    def log_p_rule(self, rule, invent=True):
        """
        give the log prior probability of a TeRF.Types.Rule

        Parameters
        ----------
        rule : TeRF.Types.Rule
            the rule whose probability is being computed
        invent : bool (default: True)
            can invent new variables if True else no new variables are allowed

        Returns
        -------
        float
            the log prior probability of `rule`
        """
        p_lhs = self.log_p(rule.lhs, invent=invent)
        self.variables = set(rule.lhs.variables)
        try:
            return p_lhs + self.log_p(rule.rhs0, invent=False)
        except AttributeError:
            raise ValueError('log_p_rule: only valid for one clause at a time')

    def sample_term_t(self, term, p_r, invent=True):
        """
        sample a TeRF.Types.Term given an existing TeRF.Types.Term

        Parameters
        ----------
        term: TeRF.Types.Term
            the given term
        p_r: float
            the node-wise probability of resampling from the prior
        invent : bool
            can invent new variables if True else no new variables are allowed
            (optional: True)

        Returns
        -------
        TeRF.Types.Term
            the resampled term
        """
        if np.random.binomial(1, p_r):
            return self.sample_term(invent)
        try:
            body = [self.sample_term_t(t, p_r, invent) for t in term.body]
            return A.App(term.head, body)
        except AttributeError:
            self.variables.add(term)
            return term

    def log_p_t(self, new, old, p_r, invent=True):
        """
        give the log prior probability of sampling a term given a term

        Parameters
        ----------
        new: TeRF.Types.Term
            the resampled term
        old: TeRF.Types.Term
            the term given when resampling `new`
        p_r: float
            the node-wise probability of resampling
        invent : bool
            can invent new variables if True else no new variables are allowed
            (optional: True)

        Returns
        -------
        float
            log(p(new | p_r, old))
        """
        p_make_head = tmisc.log(p_r) + self.log_p(new, invent)
        if new.head == old.head:
            p_keep_head = tmisc.log(1.-p_r)
            try:
                for tn, to in ittl.izip(new.body, old.body):
                    p_keep_head += self.log_p_t(tn, to, p_r, invent)
            except AttributeError:
                self.variables.add(new)
            return sm.logsumexp([p_keep_head, p_make_head])
        return p_make_head





    def sample_grammar(self, p_rule, invent=True):
        """
        sample a grammar

        Parameters
        ----------
        p_rule : float
            the probability of adding another rule
        invent : bool
            can invent new variables if True else no new variables are allowed
            (optional: True)

        Returns
        -------
        TeRF.Types.TRS
            the sampled TRS
        """
        n = stats.geom.rvs(p_rule)-1
        trs = TRS.TRS(signature=self.signature)
        while trs.num_rules() < n:
            trs.add(self.sample_rule(invent=invent))
        return trs

    def log_p_atom(self, atom, env=None):
        """
        give the log-probability of sampling a particular atom

        Parameters
        ----------
        atom : TeRF.Types.Atom
            the atom whose probability is being computed
        env : TeRF.Types.Environment (default: None)
            the set of bound and free variables

        Returns
        -------
        float
            log(p(atom | self, env))
        """
        if atom in self.signature:
            return tmisc.log(self.probs[atom])
        if invent and isinstance(atom, V.Var):
            return tmisc.log(self.probs['var']) - \
                tmisc.logNof(list(self.variables) + ['var'])
        if atom in self.variables:
            return tmisc.log(self.probs['var']) - \
                tmisc.logNof(list(self.variables))
        return tmisc.log(0)
