class LOT(object):
    """
    a representation for Languages of Thought (LOT; Fodor, 1975)

    LOT = first-order Term Rewriting Systems (TRS) + Hindley-Milner typesystem.
    """
    def __init__(self, typesystem, trs):
        """
        TODO
        ----
        - make arguments optional?
        - make the arguments consistent with one another (non-zero prob.)
        - enforce any type constraints on the arguments?
        """
        self.syntax = typesystem
        self.semantics = trs

    def __repr__(self):
        return 'LOT(typesystem={!r}, trs={!r})'.format(self.syntax,
                                                       self.semantics)

    def __str__(self):
        syntax = '\n'.join('{}: {}'.format(k, v)
                           for k, v in self.syntax.items())
        return '\n\n'.join([syntax, str(self.semantics)])
