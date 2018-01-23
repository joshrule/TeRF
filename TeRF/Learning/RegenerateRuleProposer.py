import copy
import LOTlib.Hypotheses.Proposers as P
import numpy as np
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Algorithms.Sampling as s
import TeRF.Algorithms.Typecheck as tc
import TeRF.Algorithms.TermUtils as te
import TeRF.Algorithms.TypeUtils as ty
import TeRF.Miscellaneous as misc
import TeRF.Types.TypeVariable as TVar
import TeRF.Types.Variable as Var


@utils.propose_value_template
def propose_value(value, **kwargs):
    rule = utils.choose_a_rule(value.semantics)
    env = copy.copy(value.syntax)
    env.update({v: TVar.TVar() for v in ru.variables(rule) if v not in env})
    places = ru.places(rule)
    place = places[np.random.choice(len(places))]
    value._regeneration_place = place
    new_rule = copy.deepcopy(rule)
    resampling_rhs = (place[0] == 'rhs')
    fulltype, new_sub, raw_subtype = ru.typecheck_subterm(rule, env, {}, place)
    subtype = ty.substitute(raw_subtype, new_sub)

    if resampling_rhs:
        forbidden = {}
    else:
        forbidden = ru.variables(rule) - vars_to_place(rule.lhs, place[1:])

    new_env = {k: v for k, v in env.items() if k not in forbidden}

    try:
        new_term, _, _ = s.sample_term(subtype, new_env, sub=new_sub,
                                       invent=(not resampling_rhs))
        try:
            new_rule = ru.replace(new_rule, place, new_term)
        except ValueError:
            raise P.ProposalFailedException('RegenerateRule: proposal failed')
    except s.SampleError:
        raise P.ProposalFailedException('RegenerateRule: proposal failed')

    alpha = ru.alpha(rule, new_rule)
    if alpha is None and new_rule not in value.semantics:
        print '# proposing', new_rule
        value.semantics.replace(rule, new_rule)
    else:
        raise P.ProposalFailedException('RegenerateRule: proposal failed')


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
        t_old = ru.place(old, place)
        t_new = ru.place(new, place)
    except ValueError:
        return -np.inf
    if t_old != t_new:
        env2 = env.copy()
        env2.update({v: TVar.TVar() for v in ru.variables(old)
                     if v not in env2})

        resampling_rhs = (place[0] == 'rhs')
        sub = {}
        _, sub = ru.typecheck_full(old, env2, sub)

        subtype = tc.typecheck(t_old, env2, sub)

        if resampling_rhs:
            forbidden_vars = {}
        else:
            forbidden_vars = ru.variables(old) - vars_to_place(old.lhs,
                                                               place[1:])
        env3 = {k: v for k, v in env2.items() if k not in forbidden_vars}
        return s.lp_term(t_new, subtype, env3, invent=(not resampling_rhs))[0]
    return -np.inf


@utils.validate_syntax
def give_proposal_log_fb(old, new, **kwargs):
    old_clauses = old.semantics.clauses
    new_clauses = new.semantics.clauses
    len_old = len(old_clauses)
    len_difference = len_old - len(new_clauses)

    if len_difference == 0:
        old_set = set(old_clauses)
        new_set = set(new_clauses)
        o_diff = old_set - new_set
        n_diff = new_set - old_set

        if len(o_diff) == len(n_diff) == 1:
            # p = choosing rule + choosing place + sampling subterm
            o_clause = o_diff.pop()
            n_clause = n_diff.pop()
            try:
                place = new._regeneration_place
            except AttributeError:
                return (-np.inf, -np.inf)
            o_places = ru.places(o_clause)
            n_places = ru.places(n_clause)
            p_rule = -misc.log(len_old)
            f = p_rule - misc.log(len(o_places)) + \
                p_resample(old.syntax, n_clause, o_clause, place)
            b = p_rule - misc.log(len(n_places)) + \
                p_resample(old.syntax, o_clause, n_clause, place)
            return (f, b)
    return (-np.inf, -np.inf)


class RegenerateRuleProposer(P.Proposer):
    """
    Proposer for regenerating a rule (NON-ERGODIC)

    For a Grammar R U {x}, give R U {x'}, where x is a rule, l -> r, x' is
    l' -> r', and either l != l' OR r != r', but not both.
    """
    def __init__(self, **kwargs):
        self.propose_value = propose_value
        self.give_proposal_log_fb = give_proposal_log_fb
        super(RegenerateRuleProposer, self).__init__(**kwargs)


if __name__ == "__main__":
    utils.test_a_proposer(propose_value, give_proposal_log_fb)
