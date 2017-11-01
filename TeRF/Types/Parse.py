import collections as coll
import itertools
import TeRF.Miscellaneous as misc
import TeRF.Types.Application as A
import TeRF.Types.Grammar as Grammar
import TeRF.Types.Variable as V


class ParseComplete(Exception):
    pass


class Parse(object):
    def __init__(self, grammar, term, start=None, place=None):
        self.grammar = grammar
        self.start = start
        self._parses = set()
        self._parsed = False
        self.term = term
        self.place = [] if place is None else place
        self._queue = coll.deque()
        self.dead_ends = set()

    def find_resample_points(self):
        rps = []
        for p in self.parses:
            for x in p.find_resample_points(self.grammar):
                if x not in rps:
                    rps.append(x)
        return rps

    def parse(self):
        if not self._parsed:
            self.__initialize_queue()
            self.__process_queue()
            self._parsed = True
        return self

    @property
    def parses(self):
        self.parse()
        return self._parses

    def __initialize_queue(self):
        if isinstance(self.term, V.Var):
            parse = ParseStep(self.term,
                              0.0,
                              self.grammar.scope.copy(),
                              self.place)
            try:
                self._queue.extend(self.__parse_in_scope_variable(parse))
            except KeyError:
                self._queue.extend(self.__parse_out_of_scope_variable(parse))
        else:
            self._queue.extend(self.__parse_application(self.term))

    def __process_queue(self):
        while True:
            try:
                self.__step()
            except ParseComplete:
                break

    def __step(self):
        try:
            parse = self._queue.popleft()
        except IndexError:
            raise ParseComplete()
        if self.start is None or parse.term == self.start:
            self._parses.add(parse)
        if parse.term not in self.dead_ends:
            steps = self.__augment_parse(parse)
            if steps == [] and \
               self.start is not None and \
               parse.term != self.start:
                self.dead_ends.add(parse.term)
            else:
                self._queue.extend(steps)

    def __parse_in_scope_variable(self, parse_step):
        nonterminal = self.grammar.scope.scope[parse_step.term]
        log_p = -misc.log(self.grammar.n_options(nonterminal))
        scope = self.grammar.scope.copy()
        return [ParseStep(nonterminal,
                          log_p,
                          scope,
                          parse_step.place,
                          children=[parse_step])]

    def __parse_out_of_scope_variable(self, parse_step):
        steps = []
        if not self.grammar.scope.locked:
            for rule in self.grammar:
                nonterminal = rule.lhs
                log_p = -misc.log(self.grammar.n_options(nonterminal))
                scope = self.grammar.scope.copy()
                scope.scope[parse_step.term] = nonterminal
                steps.append(ParseStep(nonterminal,
                                       log_p,
                                       self.grammar.scope.copy(),
                                       parse_step.place,
                                       down_scope=scope,
                                       children=[parse_step]))
        return steps

    def __parse_application(self, term):
        if term.head.arity == 0:
            return [ParseStep(term,
                              0.0,
                              self.grammar.scope.copy(),
                              self.place)]
        branch_parses = self.__parse_branches(term)
        return (self.__combine_branch_parses(term.head, branch_parses))

    def __parse_branches(self, term):
        body_parses = [[p] for p in Parse(self.grammar,
                                          term.body[0],
                                          place=self.place + [0]).parses]
        for i, b in enumerate(term.body[1:], 1):
            tmp = []
            for bp in body_parses:
                with Grammar.scope(self.grammar, scope=bp[-1].down_scope):
                    new_place = self.place + [i]
                    tmp += [bp + [p]
                            for p in Parse(self.grammar, b,
                                           place=new_place).parses]
            body_parses = tmp[:]
        return body_parses

    def __combine_branch_parses(self, head, branch_parses):
        parses = []
        for body in branch_parses:
            scope = body[-1].down_scope.copy()
            log_p = sum(b.log_p for b in body)
            term = A.App(head, [b.term for b in body])
            parses.append(ParseStep(term,
                                    log_p,
                                    self.grammar.scope.copy(),
                                    self.place,
                                    down_scope=scope,
                                    children=body))
        return parses

    def __augment_parse(self, parse_step):
        parses = []
        for clause in self.grammar.clauses:
            if parse_step.term == clause.rhs0:
                log_p = parse_step.log_p - \
                        misc.log(self.grammar.n_options(clause.lhs))
                parses.append(ParseStep(clause.lhs,
                                        log_p,
                                        parse_step.up_scope.copy(),
                                        parse_step.place,
                                        down_scope=parse_step.down_scope.copy(),
                                        children=[parse_step]))
        return parses


class ParseStep(object):
    def __init__(self, term, log_p, scope, place, children=None,
                 down_scope=None):
        self.log_p = log_p
        self.term = term
        self.up_scope = scope.copy()
        self.down_scope = scope.copy() if down_scope is None else down_scope
        self.place = place
        self.children = [] if children is None else list(children)

    def __repr__(self):
        return str(self)

    def __str__(self):
        string = '(lp: {:.3f}, t: {}, ds: {}, us: {})'
        return string.format(self.log_p,
                             self.term.to_string(),
                             self.down_scope,
                             self.up_scope)

    def find_resample_points(self, grammar):
        points = []
        if grammar.n_options(self.term) > 1:
            points.append((tuple(self.place), self.term, self.up_scope))
        for c in self.children:
            for p in c.find_resample_points(grammar):
                if p not in points:
                    points.append(p)
        return set(points)


class RuleParse(object):
    def __init__(self, grammar, rule, start=None):
        self.grammar = grammar
        self.start = start
        self._parses = set()
        self._parsed = False
        self.rule = rule
        self._queue = coll.deque()

    @property
    def parses(self):
        self.parse()
        return self._parses

    def parse(self):
        if self._parsed:
            return self

        with Grammar.scope(self.grammar):
            lhs_parses = Parse(self.grammar,
                               self.rule.lhs,
                               place=['l'],
                               start=self.start).parses
        start_scope_combos = {(p.term, p.down_scope) for p in lhs_parses}
        for combo in start_scope_combos:
            partial_parses = []
            for rhs in self.rule.rhs:
                with Grammar.scope(self.grammar, scope=combo[1], lock=True):
                    partial_parses.append(Parse(self.grammar,
                                                rhs,
                                                place=['r', rhs],
                                                start=combo[0]).parses)
            rhs_parses = set(itertools.product(*partial_parses))
            for lhs_parse in lhs_parses:
                if lhs_parse.term == combo[0] and \
                   lhs_parse.down_scope == combo[1]:
                    self._parses |= {(lhs_parse, rhs_parse)
                                     for rhs_parse in rhs_parses}

        self._parsed = True
        return self

    def find_resample_points(self):
        parse_trees = list(itertools.chain(*[list({p[0]} | set(p[1]))
                                             for p in self.parses]))
        rps = []
        for p in parse_trees:
            for x in p.find_resample_points(self.grammar):
                if x not in rps:
                    rps.append(x)
        return set(rps)


if __name__ == "__main__":
    import TeRF.Test.test_grammars as tg

    g = tg.head_pcfg
    start = tg.f(tg.START)

    t = tg.X
    print
    pt = Parse(grammar=g, term=t, start=start)
    print 'parses for X'
    for p in pt.parses:
        print p

    print
    with Grammar.scope(g):
        g.scope.scope[tg.X] = tg.f(tg.NUMBER)
        pt = Parse(grammar=g, term=t, start=start)
        print 'parses for X (X : Number)'
        for p in pt.parses:
            print p

    t = tg.f(tg.NIL)
    print
    pt = Parse(grammar=g, term=t, start=start)
    print 'parses for Nil'
    for p in pt.parses:
        print p

    t = tg.f(tg.CONS)
    print
    pt = Parse(grammar=g, term=t, start=t)
    print 'parses for CONS'
    for p in pt.parses:
        print p

    t = tg.g(tg.g(tg.f(tg.CONS), tg.f(tg.ONE)), tg.f(tg.NIL))
    print
    pt = Parse(grammar=g, term=t, start=start)
    print 'parses for', t.to_string()
    for p in pt.parses:
        print p

    t = tg.g(tg.g(tg.f(tg.CONS), tg.X), tg.Y)
    print
    pt = Parse(grammar=g, term=t, start=start)
    print 'parses', t.to_string()
    for p in pt.parses:
        print p
    print '\n', 'resample points'
    for rp in pt.find_resample_points():
        print rp

    t = tg.g(tg.g(tg.f(tg.CONS), tg.X), tg.X)
    print
    pt = Parse(grammar=g, term=t, start=start)
    print 'parses for', t.to_string()
    for p in pt.parses:
        print p

    r = tg.head_rule
    print
    pt = RuleParse(g, r, start=start)
    print 'parses for', r
    for p in pt.parses:
        print p
    print '\n', 'resample points'
    for rp in pt.find_resample_points():
        print rp
