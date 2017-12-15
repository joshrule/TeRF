import copy
import os
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as misc
import numpy as np
import TeRF.Types.Rule as R
import inspect


def test_a_proposer(propose_value, give_proposal_log_p, lot=None):
    import TeRF.Examples as tg
    failures = 0
    successes = 0
    while successes < 20 and failures < 10:
        if lot is None:
            value = tg.head_lot
        elif lot is 'tail':
            value = tg.tail_lot
        elif lot is 'simple':
            value = tg.simple_head_lot
        if successes == 0 and failures == 0:
            print 'initial hypothesis:\n', value, '\n'
        try:
            hyp = propose_value(value)
            log_p = give_proposal_log_p(value, hyp)
            fb = log_p - give_proposal_log_p(hyp, value)
            print '{:d}: fb={:.2f}, log_p={:.2f}'.format(successes, fb, log_p)
            print hyp.semantics, '\n'
            successes += 1
        except P.ProposalFailedException:
            print 'failed ({:d})!\n'.format(failures)
            failures += 1


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


def validate_syntax(proposal_log_p):
    def wrapper(old, new, **kwargs):
        if old.syntax == new.syntax:
            return proposal_log_p(old, new, **kwargs)
        return misc.log(0)
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


def find_difference(g1, g2):
    g1_rules = {rule for rule in g1.clauses if rule not in g2}
    g2_rules = {rule for rule in g2.clauses if rule not in g1}
    if len(g1_rules) == len(g2_rules) == 1:
        return g1_rules.pop(), g2_rules.pop()
    return (None, None)
