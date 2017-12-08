import TeRF.Types.Application as App
import TeRF.Types.Variable as Var


def substitute(term, sub):
    if isinstance(term, Var.Var):
        try:
            return sub[term]
        except KeyError:
            return term
        except TypeError:
            raise ValueError('bad substitution: {}'.format(sub))
    elif isinstance(term, App.App):
        if sub is None:
            raise ValueError('bad substitution: None')
        return App.App(term.head, [substitute(a, sub) for a in term.args])
    raise TypeError('not a term')
