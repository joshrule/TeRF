import collections as coll
import itertools
import TeRF.Types.Application as A
import TeRF.Types.Scope as Scope
import TeRF.Types.Variable as V
import TeRF.Miscellaneous as misc


class ParseComplete(Exception):
    pass


class Parse(object):
    def __init__(self, grammar, term, start=None):
        self.grammar = grammar
        self.start = start
        self.parses = set()
        self.term = term
        self._queue = coll.deque()
        # self._queue.append(ParseStep(term, 0.0, grammar.scope.copy()))
        self.dead_ends = set()

    def parse(self):
        self.__initialize_queue()
        self.__process_queue()
        return self

    def __initialize_queue(self):
        if isinstance(self.term, V.Var):
            parse = ParseStep(self.term, 0.0, self.grammar.scope.copy())
            try:
                self._queue.extend(self.__parse_in_scope_variable(parse))
            except KeyError:
                self._queue.extend(self.__parse_out_of_scope_variable(parse))
        else:
            self._queue.extend(self.__parse_application(self.term))

    def __process_queue(self):
        while True:
            try:
                self.step()
            except ParseComplete:
                break

    def step(self):
        # print 'step, where _queue:'
        # for item in self._queue:
        #     print item
        try:
            parse = self._queue.popleft()
        except IndexError:
            raise ParseComplete()
        if self.start is None or parse.term == self.start:
            self.parses.add(parse)
        if parse.term not in self.dead_ends:
            steps = self.__augment_parse(parse)
            if steps == [] and \
               self.start is not None and \
               parse.term != self.start:
                self.dead_ends.add(parse.term)
            else:
                self._queue.extend(steps)

    def n_options(self, nonterminal):
        return (len(self.grammar[nonterminal]) +
                len(self.grammar.scope.find(nonterminal)) +
                int(not self.grammar.scope.locked))

    def __parse_in_scope_variable(self, parse_step):
        nonterminal = self.grammar.scope.scope[parse_step.term]
        log_p = -misc.log(self.n_options(nonterminal))
        scope = self.grammar.scope.copy()
        return [ParseStep(nonterminal, log_p, scope, children=[parse_step])]

    def __parse_out_of_scope_variable(self, parse_step):
        steps = []
        if not self.grammar.scope.locked:
            for rule in self.grammar:
                nonterminal = rule.lhs
                log_p = -misc.log(self.n_options(nonterminal))
                scope = self.grammar.scope.copy()
                scope.scope[parse_step.term] = nonterminal
                steps.append(ParseStep(nonterminal, log_p, scope,
                                       children=[parse_step]))
        return steps

    def __parse_application(self, term):
        # print 'parsing', term.to_string()
        if term.head.arity == 0:
            return [ParseStep(term, 0.0, self.grammar.scope.copy())]
        branch_parses = self.__parse_branches(term)
        return (self.__combine_branch_parses(term.head, branch_parses))

    def __parse_branches(self, term):
        subparses = []
        for b in term.body:
            with Grammar.scope(self.grammar):
                parses = {p for p in Parse(self.grammar, b).parse().parses}
            subparses.append(list(parses))
        return subparses

    def __combine_branch_parses(self, head, branch_parses):
        parses = []
        for body in itertools.product(*branch_parses):
            scope = Scope.merge_scopes([b.scope for b in body])
            if scope is not None:
                log_p = sum(b.log_p for b in body)
                term = A.App(head, [b.term for b in body])
                parses.append(ParseStep(term, log_p, scope, children=body))
        return parses

    def __augment_parse(self, parse_step):
        # print 'augmenting'
        parses = []
        for clause in self.grammar.clauses:
            if parse_step.term == clause.rhs0:
                log_p = parse_step.log_p - misc.log(self.n_options(clause.lhs))
                parses.append(ParseStep(clause.lhs,
                                        log_p,
                                        parse_step.scope,
                                        children=[parse_step]))
        return parses


class ParseStep(object):
    def __init__(self, term, log_p, scope, children=None):
        self.log_p = log_p
        self.term = term
        self.scope = scope
        self.children = [] if children is None else list(children)

    def __str__(self):
        return '(lp: {:.3f}, t: {}, s: {})'.format(self.log_p,
                                                   self.term.to_string(),
                                                   self.scope)


if __name__ == "__main__":
    import TeRF.Test.test_grammars as tg
    import TeRF.Types.Grammar as Grammar

    g = tg.head_pcfg
    start = tg.f(tg.START)

    t = tg.X
    print
    pt = Parse(grammar=g, term=t, start=start).parse()
    print 'parses for X'
    for p in pt.parses:
        print p

    print
    with Grammar.scope(g):
        g.scope.scope[tg.X] = tg.f(tg.NUMBER)
        pt = Parse(grammar=g, term=t, start=start).parse()
        print 'parses for X (X : Number)'
        for p in pt.parses:
            print p

    t = tg.f(tg.NIL)
    print
    pt = Parse(grammar=g, term=t, start=start).parse()
    print 'parses for Nil'
    for p in pt.parses:
        print p

    t = tg.f(tg.CONS)
    print
    pt = Parse(grammar=g, term=t, start=t).parse()
    print 'parses for CONS'
    for p in pt.parses:
        print p

    t = tg.g(tg.g(tg.f(tg.CONS), tg.f(tg.ONE)), tg.f(tg.NIL))
    print
    pt = Parse(grammar=g, term=t, start=start).parse()
    print 'parses for', t.to_string()
    for p in pt.parses:
        print p

    t = tg.g(tg.g(tg.f(tg.CONS), tg.X), tg.Y)
    print
    pt = Parse(grammar=g, term=t, start=start).parse()
    print 'parses', t.to_string()
    for p in pt.parses:
        print p

    t = tg.g(tg.g(tg.f(tg.CONS), tg.X), tg.X)
    print
    pt = Parse(grammar=g, term=t, start=start).parse()
    print 'parses', t.to_string()
    for p in pt.parses:
        print p
