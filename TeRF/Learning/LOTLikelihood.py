import numpy as np
import TeRF.Miscellaneous as misc
import TeRF.Types.TRS as TRS
import TeRF.Types.Trace as T


class LOTLikelihood(object):
    def compute_single_likelihood(self, datum):
        """
        the log likelihood of the hypothesis for a single datum

        This likelihood is semi-generative. It assumes the existence of
        datum.lhs and then asks how likely datum.rhs0 is to be generated
        from datum.lhs given the rules and assumed observation frequency.

        Notes
        -----
        - compute_likelihood manages likelihood_temperature. It's ignored here.

        Assumes
        -------
        self.value: an attribute of the hypothesis
        self.p_partial: an attribute of the hypothesis
        self.temperature: an attribute of the hypothesis

        Parameters
        ----------
        datum: TeRF.Types.Rule
            a single datum

        Returns
        -------
        float
            -inf <= x <= 0, log p(datum | self.value)
        """
        # combine the background knowledge and hypothesis
        combined_trs = TRS.TRS()
        try:
            for clause in reversed(self.background.clauses):
                combined_trs.add(clause)
        except AttributeError:
            combined_trs = self.value.semantics
        else:
            for clause in reversed(self.value.semantics.clauses):
                combined_trs.add(clause)

        # run the trace and collect the ll
        t = T.Trace(combined_trs, datum.lhs,
                    p_observe=0.0, max_steps=20).run()
        ll = t.rewrites_to(datum.rhs0)

        # assign partial credit
        partial_credit = self.p_partial + self.temperature
        real_pc = self.p_partial + self.real_temperature

        # report the results
        if ll == -np.inf:
            result = misc.log(partial_credit)
            real_result = misc.log(real_pc)
        else:
            result = misc.log(1.-partial_credit) + ll
            real_result = misc.log(1.-real_pc) + ll
        return (result, real_result)


if __name__ == '__main__':
    import TeRF.Examples as tg

    ll = LOTLikelihood()
    ll.temperature = 0.0
    ll.p_partial = 0.0

    def test_likelihood(hypothesis, data):
        ll.value = hypothesis
        print '\nhypothesis:\n', ll.value
        for datum in data:
            log_p = ll.compute_single_likelihood(datum)
            print '\ndatum:', datum
            print 'll:', log_p
            if log_p == -np.inf:
                print '1/exp(ll): inf'
            else:
                print '1/exp(ll):', 1./np.exp(log_p)

    lot_with_vars = tg.head_lot
    test_likelihood(lot_with_vars, [tg.head_datum_T,
                                    tg.head_datum_F])
