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
        self.semantics = trs.make_deterministic()

    def __repr__(self):
        return 'LOT(typesystem={!r}, trs={!r})'.format(self.syntax,
                                                       self.semantics)

    def __eq__(self, other):
        return (self.semantics == other.semantics and
                self.syntax == other.syntax)

    def __ne__(self, other):
        return self != other

    def __str__(self):
        return '\n' + str(self.semantics)

    @property
    def size(self):
        return self.semantics.size
