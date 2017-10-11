import LOTlib.Miscellaneous as lmisc
import numpy as np
import scipy as sp
import TeRF.Miscellaneous as tmisc
import TeRF.Learning.TRSGrammar as TRSG


def counts_to_probs(counts):
    ops, counts = tuple(zip(*counts.items()))
    probs = np.random.dirichlet(counts)
    return {op: prob for op, prob in zip(ops, probs)}


def merge_counts(c1, c2):
    c3 = c1.copy()
    for k, v in c2.items():
        if k in c3:
            c3[k] += v
        else:
            c3[k] = v
    return c3


def update_counts(counts, atoms, invent=True):
    for atom in atoms:
        if hasattr(atom, 'arity'):
            counts[atom] += 1
        else:
            counts['var'] += 1
    return counts


def compute_rr_term(top_counts, bottom_counts):
    return (lmisc.beta(top_counts.values()) -
            lmisc.beta(bottom_counts.values()))


class RationalRulesTRSGrammar(object):
    """
    Sample TeRF.Types.Term objects from a Rational Rules-style prior.

    - Credit to Kevin Ellis for the basic split between the context-free PCFG
      and the context-sensitive variable management

    Parameters
    ----------
    signature : TeRF.Types.Signature
        a collection of operators for sampling applicative terms
    variables : set of TeRF.Types.Variable
        a collection of variables for sampling variable terms.
    counts : dict of TeRF.Types.Operator keys and int values (optional: None)
        the prior vector
    invent : bool (default: True)
        can invent new variables if True, else no new variables are allowed
    alpha : float (optional: 1.0)
        the value to use when extending the prior for variables

    """
    def __init__(self, signature, counts=None, invent=True, alpha=1.0):
        self.signature = signature
        self.variables = set()
        self.invent = invent
        self.alpha = alpha

        if counts is None:
            self.counts = {op: self.alpha for op in signature.operators}
        else:
            self.counts = counts

        if self.invent or self.variables and 'var' not in self.counts:
            self.counts['var'] = self.alpha

    def compute_var_term(self, atoms):
        '''
        Compute the probability of sampling the variables in a term

        Parameters
        ----------
        atoms : list of TeRF.Types.Atom
            the atoms composing a term (in-order traversal)
        '''
        lp = 0.0
        for atom in atoms:
            if not hasattr(atom, 'arity'):
                lp -= tmisc.log(len(self.variables) +
                                (1 if self.invent else 0))

                if self.invent and atom not in self.variables:
                    self.variables.add(atom)
                elif not self.invent and atom not in self.variables:
                    return -np.inf
        return lp

    def sample_atom(self):
        """
        sample an atom

        Returns
        -------
        TeRF.Types.Atom
            either an operator or a variable
        """
        prod_probs = counts_to_probs(self.counts)
        return TRSG.TRSGrammar(self.signature,
                               variables=self.variables,
                               probs=prod_probs).sample_atom(invent=self.invent)

    def log_p_atom(self, atom):
        """
        give the log prior probability of sampling a particular atom

        Parameters
        ----------
        atom : TeRF.Types.Atom
            the atom whose probability is being computed

        Returns
        -------
        float
            the log prior probability of `atom`
        """
        top_counts = update_counts(self.counts.copy(),
                                   [atom],
                                   invent=self.invent)
        cflp = compute_rr_term(top_counts, self.counts)
        cslp = self.compute_var_term([atom])
        return cflp + cslp

    def sample_term(self):
        """
        sample a TeRF.Types.Term

        Returns
        -------
        TeRF.Types.Term
            a term sampled from the grammar according to the prior
        """
        prod_probs = counts_to_probs(self.counts)
        return TRSG.TRSGrammar(self.signature,
                               variables=self.variables,
                               probs=prod_probs).sample_term(invent=self.invent)

    def log_p(self, term):
        """
        give the log-probability of sampling a term

        Parameters
        ----------
        term : TeRF.Types.Term
            the term whose log prior probability we're computing

        Returns
        -------
        p : float
            the log prior probability of `term`
        """
        atoms = [t.head for t in term.subterms]
        top_counts = update_counts(self.counts.copy(),
                                   atoms,
                                   invent=self.invent)
        cflp = compute_rr_term(top_counts, self.counts)
        cslp = self.compute_var_term(atoms)
        return cflp + cslp

    def sample_rule(self):
        """
        sample a TeRF.Types.Rule

        Returns
        -------
        TeRF.Types.Rule
            a rule sampled from the grammar according to the prior
        """
        prod_probs = counts_to_probs(self.counts)
        return TRSG.TRSGrammar(self.signature,
                               variables=self.variables,
                               probs=prod_probs).sample_rule(invent=self.invent)

    def log_p_rule(self, rule):
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
        top_counts = self.counts.copy()
        for r in rule:
            top_counts = update_counts(top_counts,
                                       [t.head for t in r.lhs.subterms],
                                       invent=self.invent)
            top_counts = update_counts(top_counts,
                                       [t.head for t in r.rhs0.subterms],
                                       invent=False)
        cflp = compute_rr_term(top_counts, self.counts)
        cslp = 0.0
        for r in rule:
            cslp += self.compute_var_term([t.head for t in r.lhs.subterms])
            invent = self.invent
            self.invent = False
            cslp += self.compute_var_term([t.head for t in r.rhs0.subterms])
            self.invent = invent
        return cflp + cslp

    def sample_term_t(self, term, p_r):
        """
        sample a term given a term by resampling random subtrees

        Parameters
        ----------
        term: TeRF.Types.Term
            the given term
        p_r: float
            the node-wise probability of resampling from the prior

        Returns
        -------
        TeRF.Types.Term
            the sampled term
        """
        prod_probs = counts_to_probs(self.counts)
        sampler = TRSG.TRSGrammar(self.signature,
                                  variables=self.variables,
                                  probs=prod_probs)
        return sampler.sample_term_t(term, p_r, invent=self.invent)

    def log_p_t(self, new, old, p_r):
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

        Returns
        -------
        float
            log(p(new | p_r, old))
        """
        vars = self.variables.copy()
        p_make_head = tmisc.log(p_r) + self.log_p(new)
        self.variables = vars
        if new.head == old.head:
            p_keep_head = tmisc.log(1.-p_r)
            try:
                for tn, to in zip(new.body, old.body):
                    p_keep_head += self.log_p_t(tn, to, p_r)
            except AttributeError:
                self.variables.add(new)
            return sp.misc.logsumexp([p_keep_head, p_make_head])
        return p_make_head

    def sample_trs(self, p_rule):
        """
        sample a TRS

        Parameters
        ----------
        p_rule : float
            the probability of adding another rule

        Returns
        -------
        TeRF.Types.TRS
            the sampled TRS
        """
        prod_probs = counts_to_probs(self.counts)
        return TRSG.TRSGrammar(self.signature,
                               variables=self.variables,
                               probs=prod_probs).sample_trs(p_rule,
                                                            invent=self.invent)

    def count_trs(self, trs):
        counts = {k: 0 for k in self.counts}
        for r in trs.rules():
            counts = update_counts(counts,
                                   [t.head for t in r.lhs.subterms],
                                   invent=self.invent)
            counts = update_counts(counts,
                                   [t.head for t in r.rhs0.subterms],
                                   invent=False)
        return counts

    def log_p_trs(self, trs, p_rule):
        """
        compute the log prior probability of a TRS

        Parameters
        ----------
        trs: TeRF.Types.TRS
            the TRS whose prior probability is being computed
        p_rule: float
            the probability of adding another rule

        Returns
        -------
        float
            log(p(trs | p_rule))
        """
        cflp = compute_rr_term(self.count_trs(trs), self.counts)
        cslp = 0.0
        for r in trs.rules():
            cslp += self.compute_var_term([t.head for t in r.lhs.subterms])
            invent = self.invent
            self.invent = False
            cslp += self.compute_var_term([t.head for t in r.rhs0.subterms])
            self.invent = invent
        return cflp + cslp + sp.stats.geom.logpmf(trs.num_rules(), p=p_rule)
