import collections
import itertools as I
import numpy as np
import TeRF.Pseudowords as P


class TRS(collections.MutableMapping):
    def save(self, filename):
        with open(filename, 'w') as f:
            f.write('signature ')
            f.write(' '.join(str(op) for op in self.signature) + ';\n')
            f.write(';\n'.join([str(rule) for rule in self])+';\n')

    def features(self):
        feats = {}
        feats['n_rules'] = self.num_rules()
        feats['n_nodes'] = sum(len(r.lhs) + len(r.rhs0) for r in self.rules())
        feats['n_lhss'] = len(self)
        feats['mean_rule_len'] = (float(feats['n_nodes']) /
                                  float(feats['n_rules']))
        feats['max_rule_len'] = max(len(r.lhs) + len(r.rhs0)
                                    for r in self.rules())
        feats['n_vars'] = sum(1 for r in self.rules()
                              for t in I.chain(r.lhs.subterms, r.rhs0.subterms)
                              if not hasattr(t, 'body'))
        feats['%_vars'] = float(feats['n_vars']) / float(feats['n_nodes'])
        feats['n_nondet_rules'] = sum(1 for r in self if len(r) > 1)
        feats['n_nondets'] = sum(len(r) for r in self if len(r) > 1)
        feats['%_nondets'] = float(feats['n_nondet_rules']) / \
            float(feats['n_lhss'])
        return feats

    def rename_operators(self, change=None):
        if change is not None:
            to_rename = [op for op in self.signature.operators if op in change]
            new_names = np.random.choice(P.pseudowords,
                                         size=len(to_rename),
                                         replace=False)
            for op, name in I.izip(to_rename, new_names):
                for rule in self.rules():
                    for term in rule.lhs.subterms:
                        if term.head == op:
                            term.head.name = name
                    for term in rule.rhs0.subterms:
                        if term.head == op:
                            term.head.name = name
                op.name = name

    def prettify(self, change=None):
        self.rename_operators(change)
        for rule in self:
            rule.rename_variables()
