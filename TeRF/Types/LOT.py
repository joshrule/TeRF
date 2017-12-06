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

    def __str__(self):
        return '\n\n'.join([str(self.syntax),
                            str(self.semantics)])


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg
    print LOT(tg.syntax, tg.semantics)
