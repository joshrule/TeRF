import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Algorithms.Sampling as s
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.TermUtils as te
import TeRF.Miscellaneous as misc
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.Variable as Var


@utils.propose_value_template
def propose_value(value, **kwargs):
    rule = utils.choose_a_rule(value.semantics)

    env = value.syntax.copy()
    env.update({v: TVar.TVar() for v in ru.variables(rule) if v not in env})
    sub = {}
    ru.typecheck(rule, env, sub)

    places = list(np.random.permutation(ru.places(rule)))

    new_rule = copy.deepcopy(rule)
    while ru.alpha(new_rule, rule) is not None:
        try:
            place = places.pop()
        except ValueError:
            raise P.ProposalFailedException('RegenerateRule: proposal failed')

        term = ru.place(rule, place)
        resampling_rhs = (place[0] == 'rhs')

        new_env = env.copy()
        new_sub = sub.copy()
        subtype = tc.typecheck(term, new_env, new_sub)

        if resampling_rhs:
            forbidden = {}
        else:
            forbidden = ru.variables(rule) - vars_to_place(rule.lhs, place[1:])
        new_env = {k: v for k, v in new_env.items() if k not in forbidden}
        new_term, _, _ = s.sample_term(subtype, new_env, sub=new_sub,
                                       invent=resampling_rhs)

        try:
            new_rule = ru.replace(new_rule, place, new_term)
        except ValueError:
            pass

    value.semantics.replace(rule, new_rule)


def vars_to_place(term, place):
    result = set()
    for p in te.places(term):
        if p == place:
            break
        subterm = te.subterm(term, p)
        if isinstance(subterm, Var.Var):
            result.add(subterm)
    return result


def p_resample(env, new, old, place):
    try:
        t_old = old.place(place)
        t_new = new.place(place)
    except ValueError:
        return -np.inf
    if t_old != t_new:
        env2 = env.copy()
        env2.update({v: TVar.TVar() for v in ru.variables(old)
                     if v not in env2})
        resampling_rhs = (place[0] == 'rhs')
        sub = {}
        ru.typecheck(old, env2, sub)

        subtype = tc.typecheck(t_old, env2, sub)

        if resampling_rhs:
            forbidden_vars = {}
        else:
            forbidden_vars = ru.variables(old) - vars_to_place(old.lhs,
                                                               place[1:])
        env3 = {k: v for k, v in env2.items() if k not in forbidden_vars}
        return s.log_p_term(t_new, subtype, env3, invent=resampling_rhs)
    return -np.inf


@utils.validate_syntax
def give_proposal_log_p(old, new, **kwargs):
    new_rule, old_rule = utils.find_difference(new.semantics, old.semantics)
    try:
        p_rule = misc.logNof(list(old.semantics.clauses))

        places = old_rule.places()

        p_t = misc.logNof(places)

        p_resamples = [p_t + p_resample(old.syntax, new_rule, old_rule, p)
                       for p in places]

        return p_rule + misc.logsumexp(p_resamples)
    except AttributeError:
        return -np.inf


class RegenerateRuleProposer(P.Proposer):
    """
    Proposer for regenerating a rule (NON-ERGODIC)

    For a Grammar R U {x}, give R U {x'}, where x is a rule, l -> r, x' is
    l' -> r', and either l != l' OR r != r', but not both.
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_p = give_proposal_log_p
        super(RegenerateRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_p)
