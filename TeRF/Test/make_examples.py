import collections
import joblib
import os
import subprocess
import sys
import TeRF.Miscellaneous as misc
import TeRF.Language.parser as parser
import TeRF.Test.run_tests as rt
import TeRF.Types.Application as A
import TeRF.Types.Variable as V
import yaml

RC = collections.namedtuple('RC', [
    'out_dir',
    'gen_theory',
    'src_dir',
    'prob_dir',
    'signature_file',
    'start_string',
    'p_operator',
    'p_arity',
    'p_rule',
    'max_nodes',
    'n_problems',
    'n_changed',
    'n_total'])


def main(rcfile):
    rc = load_config(rcfile, RC)

    e_trss = misc.find_files(rc.src_dir) + rt.sample_problems(rc)
    
    g_trs, _ = parser.load_source(rc.gen_theory)

    s = A.App(g_trs.signature.find(rc.start_string), [])

    joblib.Parallel(n_jobs=-1)(
        joblib.delayed(make_example)(e_trs, g_trs, s, rc, i)
        for i, e_trs in enumerate(e_trss))


def load_config(rcfile, rc_obj):
    with open(rcfile, 'r') as the_file:
        return rc_obj(**yaml.safe_load(the_file))


def make_example(e_trs_f, g_trs, s, rc, idx):
    e_trs, _ = parser.load_source(e_trs_f, signature=g_trs.signature.copy())
    data = rt.make_data(e_trs, g_trs, rc.n_changed, rc.n_total, s, quiet=True)
    write_output(rc, e_trs, data, idx)
    # write_fancy_output(rc, e_trs, data, idx)


def make_colormap(symbols):
    colors = ['r', 'g', 'b', 'k', 'y', 'c', 'm', 'w']
    if len(symbols) > len(colors):
        raise ValueError
    return {s: c for s, c in zip(list(symbols, colors))}


def write_output(rc, trs, data, idx):
    out_f = misc.mkdir(os.path.join(rc.out_dir, str(idx) + '.terf'))
    with open(out_f, 'w') as f:
        f.write('TRS:\n\n')
        f.write(str(trs) + '\n\n\n')
        f.write('Data:\n\n')
        for datum in data:
            f.write(str(datum) + '\n')


def write_fancy_output(rc, trs, data, idx):
    n_rules = trs.num_rules() + len(data)

    for i, rule in enumerate(data+list(trs.rules())):
        lhs, rhs = rule.to_dot()

        lhs_file = os.path.abspath(os.path.join(rc.out_dir, 'lhs_' + str(i)))
        lhs.save(lhs_file + '.dot')
        subprocess.call(('dot2tex ' + lhs_file + '.dot > ' + lhs_file + '.tex').split())
        subprocess.call(('pdflatex ' + lhs_file + '.tex').split())

        rhs_file = os.path.abspath(os.path.join(rc.out_dir, 'rhs_' + str(i)))
        rhs.save(rhs_file + '.dot')
        subprocess.call(('dot2tex ' + rhs_file + '.dot > ' + rhs_file + '.tex').split())
        subprocess.call(('pdflatex ' + rhs_file + '.tex').split())

        rule_file = os.path.join(rc.out_dir, 'rule_' + str(i) + '.text')
        with open(rule_file, 'w') as f:
            f.write(str(rule))


def color(node, colormap):
    if isinstance(node, V.Variable):
        return '#888888'
    return colormap[node.name]


# def to_graph(term, G=None, pos=None):
#     if G is None:
#         G = nx.DiGraph()
#     if pos is None:
#         pos = (0,)
#
#     if isinstance(term, V.Variable):
#         root = (pos, term)
#         G.add_node(root)
#         return (G, root)
#
#     elif isinstance(term, A.Application):
#         root = (pos, term.head)
#         G.add_node(root)
#         for p, b in enumerate(term.body):
#             G, r = to_graph(b, G, pos+(p,))
#             G.add_edge(root, r)
#         return G, root
#
#     else:
#         raise ValueError('not a Term')


if __name__ == '__main__':
    main(sys.argv[1])
