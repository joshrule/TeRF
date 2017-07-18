import TeRF.Types.Variable as V
import TeRF.Types.Operator as O
import TeRF.Types.Application as A
import TeRF.Types.Rule as R
import TeRF.Types.TRS as TRS

s = O.Op('S', 0)
print 'S:', s
k = O.Op('K', 0)
print 'K:', k
app = O.Op('.', 2)
print '.:', app

trs = TRS.TRS()
trs.signature |= {app, s, k}

x = V.Var('x')
print 'x:', x
y = V.Var('y')
print 'y:', y
z = V.Var('z')
print 'z:', z

lhs1 = A.App(app, [A.App(app, [A.App(k, []), x]), y])
print 'lhs1:', lhs1.pretty_print()
rhs1 = x
print 'rhs1:', rhs1.pretty_print()
rule1 = R.Rule(lhs1, rhs1)
print 'rule1', rule1

lhs2 = A.App(app, [A.App(app, [A.App(app, [A.App(s, []), x]), y]), z])
rhs2 = A.App(app, [A.App(app, [x, z]), A.App(app, [y, z])])
rule2 = R.Rule(lhs2, rhs2)

trs[0] = rule1
trs[1] = rule2

term = A.App(app,
             [A.App(app,
                    [A.App(app,
                           [A.App(k, []),
                            A.App(s, [])]),
                     A.App(k, [])]),
              A.App(s, [])])

print 'term:', term.pretty_print()

outcomes = term.rewrite(trs, max_steps=5, trace=False, type='all')

if isinstance(outcomes, (list, tuple, set)):
    for o in outcomes:
        print o.pretty_print()

trace = term.rewrite(trs, max_steps=5, trace=True)
