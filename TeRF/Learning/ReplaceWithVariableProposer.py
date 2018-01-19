import numpy as np
import LOTlib.Hypotheses.Proposers as P
import TeRF.Miscellaneous as misc
import TeRF.Learning.ProposerUtilities as utils
import TeRF.Algorithms.RuleUtils as ru
import TeRF.Algorithms.TermUtils as te
import TeRF.Types.Application as App
import TeRF.Types.Variable as V


def replace(term, k, v):
    if term == k:
        return v
    try:
        return App.App(term.head, [replace(arg, k, v) for arg in term.args])
    except AttributeError:
        return term


@utils.propose_value_template
def propose_value(value, **kwargs):
    # choose a rule
    rule = utils.choose_a_rule(value.semantics)

    # choose a subterm (but don't allow entire lhs to be replaced)
    places = te.places(rule.lhs)[1:]
    try:
        place = places[np.random.choice(len(places))]
    except ValueError:
        raise P.ProposalFailedException('cannot replace with variable')
    value._replacement_place = ['lhs'] + place
    subterm = te.subterm(rule.lhs, place)

    # invent a variable
    var = V.Variable()

    # perform a replacement
    lhs = replace(rule.lhs, subterm, var)
    rhs = replace(rule.rhs0, subterm, var)
    try:
        new_rule = utils.make_a_rule(lhs, rhs)
    except ValueError:
        raise P.ProposalFailedException('bad rule')

    if new_rule in value.semantics:
        raise P.ProposalFailedException('rule already exists')
    return value.semantics.replace(rule, new_rule)


@utils.validate_syntax
def give_proposal_log_fb(old, new, **kwargs):
    old_clauses = old.semantics.clauses
    new_clauses = new.semantics.clauses
    len_old = len(old_clauses)

    if len_old == len(new_clauses):
        old_set = set(old_clauses)
        new_set = set(new_clauses)
        o_diff = old_set - new_set
        n_diff = new_set - old_set

        if len(o_diff) == len(n_diff) == 1:
            # p = choosing rule + choosing place + valid replacement
            o_clause = o_diff.pop()
            n_clause = n_diff.pop()
            try:
                place = new._replacement_place
            except AttributeError:
                return (-np.inf, -np.inf)
            o_places = ru.places(o_clause)
            n_places = ru.places(n_clause)
            p_rule = -misc.log(len_old)
            try:
                f_term = ru.place(o_clause, place)
                b_term = ru.place(n_clause, place)
            except ValueError:
                return (-np.inf, -np.inf)

            try:
                f_pairs = [(ru.place(o_clause, p), ru.place(n_clause, p))
                           for p in o_places
                           if ru.place(o_clause, p) == f_term]
                f_valid = (0 if all(x == (f_term, b_term) for x in f_pairs)
                           else -np.inf)
            except ValueError:
                f_valid = -np.inf

            try:
                b_pairs = [(ru.place(n_clause, p), ru.place(o_clause, p))
                           for p in n_places
                           if ru.place(n_clause, p) == b_term]
                b_valid = (0 if all(x == (b_term, f_term) for x in b_pairs)
                           else -np.inf)
            except ValueError:
                b_valid = -np.inf

            f = p_rule - misc.log(len(te.places(o_clause.lhs))-1) + f_valid
            b = p_rule - misc.log(len(te.places(n_clause.lhs))-1) + b_valid
            return (f, b)
    return (-np.inf, -np.inf)


class ReplaceWithVariableProposer(P.Proposer):
    """
    Proposer for replacing a constant with a variable (NON-ERGODIC FOR TRSs)

    Given a TRS (S,R U {r}), give a new TRS (S, R U {r'}), where r is a Rule,
    and r' is r with one of its subterms replaced with a variable.
    """
    def __init__(self, **kwargs):
        """Create an AddRuleProposer"""
        self.propose_value = propose_value
        self.give_proposal_log_fb = give_proposal_log_fb
        super(ReplaceWithVariableProposer, self).__init__(**kwargs)
