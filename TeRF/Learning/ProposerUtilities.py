import LOTlib.Hypotheses.Proposers as P
import numpy as np

import TeRF.Types.Rule as R


def choose_a_rule(trs):
    try:
        return np.random.choice(list(trs.rules()))
    except ValueError:
        raise P.ProposalFailedException('choose_a_rule: TRS has no rules')


def make_a_rule(lhs, rhs):
    try:
        return R.Rule(lhs, rhs)
    except ValueError:
        raise P.ProposalFailedException('make_a_rule: bad rule')
