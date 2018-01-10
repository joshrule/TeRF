import copy
import os
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Types.Rule as R
import inspect


def test_a_proposer(propose_value, give_proposal_log_p, lot=None):
    import TeRF.Examples as tg
    failures = 0
    successes = 0
    while successes < 50 and failures < 20:
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


def validate_syntax(proposal_f):
    def wrapper(old, new, **kwargs):
        if old.syntax == new.syntax:
            return proposal_f(old, new, **kwargs)
        return (-np.inf, -np.inf)
    return wrapper


def propose_value_template(propose_value):
    def wrapper(value, **kwargs):
        new_value = copy.deepcopy(value)
        propose_value(new_value, **kwargs)
        src_filename = os.path.basename(inspect.getsourcefile(propose_value))
        print '#', os.path.splitext(src_filename)[0]
        return new_value
    return wrapper
