import copy
import os
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as misc
import numpy as np
import TeRF.Types.Rule as R
import TeRF.Test.test_grammars as tg
import inspect


def test_a_proposer(propose_value, give_proposal_log_p, lot=None):
    for i in xrange(20):
        if lot is None:
            value = tg.head_lot
        elif lot is 'headtail':
            value = tg.headtail_lot
        if i == 0:
            print 'initial hypothesis:\n', value, '\n'
        hyp = propose_value(value)
        log_p = give_proposal_log_p(value, hyp)
        fb = log_p - give_proposal_log_p(hyp, value)
        print '{:d}: fb={:.2f}, log_p={:.2f}'.format(i, fb, log_p)
        print hyp.semantics, '\n'


def choose_a_rule(g, f=None):
    try:
        return np.random.choice([r for r in g.clauses if (f is None) or f(r)])
    except ValueError:
        raise P.ProposalFailedException('choose_a_rule: Grammar has no rules')


def make_a_rule(lhs, rhs):
    try:
        return R.Rule(lhs, rhs)
    except ValueError:
        raise P.ProposalFailedException('make_a_rule: bad rule')


def validate_syntax_and_primitives(proposal_log_p):
    def wrapper(old, new, **kwargs):
        if old.primitives == new.primitives and \
           old.syntax == new.syntax:
            val = proposal_log_p(old, new, **kwargs)
        if val is None:
            val = misc.log(0)
        return val
    return wrapper


def propose_value_template(propose_value):
    def wrapper(value, **kwargs):
        new_value = copy.deepcopy(value)
        propose_value(new_value, **kwargs)
        src_filename = os.path.basename(inspect.getsourcefile(propose_value))
        print '#', os.path.splitext(src_filename)[0]
        return new_value
    return wrapper


def find_insertion(g1, g2):
    """if g1 == (g2 + rule), return rule, else None"""
    new_rules = {rule for rule in g1.clauses if rule not in g2}
    if len(new_rules) == 1:
        rule = new_rules.pop()
        g1prime = copy.deepcopy(g1)
        del g1prime[rule]
        if g1prime == g2:
            return rule


def there_was_a_move(g1, g2):
    g1_rules = {c for c in g1.clauses if c not in g2}
    g2_rules = {c for c in g2.clauses if c not in g1}
    if g1_rules == g2_rules == set():
        new_order = [g2._order.index(key)
                     for key in g1._order]
        monotonic = [new_order[i] < new_order[i+1]
                     for i in xrange(len(new_order)-1)]
        if monotonic.count(False) == 1:
            return True
        return False

# def find_difference(self, other):
#     s_rules = {rule for rule in self.rules() if rule not in other}
#     o_rules = {rule for rule in other.rules() if rule not in self}
#     if len(s_rules) == len(o_rules) == 1:
#         return s_rules.pop(), o_rules.pop()
#     return (None, None)
