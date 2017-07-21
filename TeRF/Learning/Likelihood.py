import TeRF.Types.Trace as T


class Likelihood(object):
    def compute_single_likelihood(self, datum):
        """
        the log likelihood of the hypothesis for a single datum

        This likelihood is generative. It asks how likely datum.lhs is to be
        generated from self.start and how likely datum.rhs is to be generated
        from datum.lhs given the rules and our assumptions about observation
        frequency.

        It ignores self.likelihood_temperature; compute_likelihood manages it.

        Assumes:
          self.value: from LOTlib.Hypotheses.Hypothesis
          self.p_observe: should be an argument to the hypothesis __init__
          self.start: the starting term
        Args:
          datum: a rewriteRule representing a single datum
        Returns: a float, -inf <= x <= 0, log p(datum | self.value)
        """
#         print 'start', self.start
#         print 'tree', self.value._order[0]
#         print 'start is tree?', self.start.head == self.value._order[0].head
#         lt = T.Trace(self.value, self.start, p_observe=self.p_observe,
#                      max_steps=5).run()
#         print [s.term.pretty_print() for s in lt.root.leaves()]
#         p_lhs = lt.rewrites_to(datum.lhs)
#         print 'p_lhs:', p_lhs
#         print 'lhs', datum.lhs.pretty_print()
#        print 'rhs', datum.rhs0.pretty_print()
        rt = T.Trace(self.value, datum.lhs, p_observe=self.p_observe,
                     max_steps=5).run()
#         print [s.term.pretty_print() for s in rt.root.leaves()]
        p_rewrite = rt.rewrites_to(datum.rhs0)
#        print 'p_rewrite:', p_rewrite
        return p_rewrite
