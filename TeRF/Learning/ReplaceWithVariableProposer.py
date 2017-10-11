import copy
import numpy as np
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as misc
import TeRF.Learning.ProposerUtilities as pu
import TeRF.Types.Application as A
import TeRF.Types.Variable as V


def replace(term, subterm, var):
    if term == subterm:
        return var
    try:
        body = [replace(b, subterm, var) for b in term.body]
        return A.App(term.head, body)
    except AttributeError:
        return term


def propose_value(value, **kwargs):
    new_value = copy.deepcopy(value)
    rule = pu.choose_a_rule(new_value)
    subterms = list(rule.lhs.subterms) + list(rule.rhs0.subterms)
    subterms = [t for t in subterms if hasattr(t, 'body')]
    if subterms == []:
        raise P.ProposalFailedException('ReplaceWithVariable: empty rule')
    subterm = np.random.choice(subterms)
    var = V.Variable()
    lhs = replace(rule.lhs, subterm, var)
    rhs = replace(rule.rhs0, subterm, var)
    new_rule = pu.make_a_rule(lhs, rhs)
    print '# rvp: changing', rule, 'to', new_rule
    return new_value.swap(rule, new_rule)


def give_proposal_log_p(old, new, **kwargs):
    print 'old == new', old.signature == new.signature
    if old.signature == new.signature:
        new_rule, old_rule = new.find_difference(old)
        print '(new, old)', new_rule, old_rule
        try:
            subterms = list(old_rule.lhs.subterms) + \
                       list(old_rule.rhs0.subterms)
            subterms = list(set([t for t in subterms if hasattr(t, 'body')]))
            var = V.Variable()
            print 'subterms', subterms
            eq_lhs = [new_rule.lhs.unify(
                replace(old_rule.lhs, t, var), type='alpha') is not None
                      for t in subterms]
            eq_rhs = [new_rule.rhs0.unify(
                replace(old_rule.rhs0, t, var), type='alpha') is not None
                      for t in subterms]
            eqs = [lhs and rhs for lhs, rhs in zip(eq_lhs, eq_rhs)]
            print 'eq_lhs', eq_lhs
            print 'eq_rhs', eq_rhs
            print 'sum lhs', sum(eq_lhs)
            print 'sum rhs', sum(eq_rhs)
            print 'eqs', eqs
            if old_rule is not None and sum(eqs) == 1:
                return misc.logNof(subterms)
        except:
            pass
    return misc.log(0)


class ReplaceWithVariableProposer(P.Proposer):
    """
    Proposer for replacing a constant with a variable (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {r}), give a new TRS (S, R U {r'}), where r is a Rule,
    and r' is r with one of its constants replaced with a variable.
    """
    def __init__(self, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(ReplaceWithVariableProposer, self).__init__(**kwargs)
