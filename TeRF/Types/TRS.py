class TypedTRS(object):
    """
    Term Rewriting Systems with Hindley-Milner types
    """
    def __init__(self, types, primitives, semantics):
        """
        TODO
        ----
        - make arguments optional?
        - are the arguments are consistent with one another (non-zero prob.)
        - enforce any type constraints on the arguments?
        """
        self.types = types
        self.primitives = primitives
        self.semantics = semantics

    def __str__(self):
        return '\n\n'.join([str(self.types),
                            str(self.primitives),
                            str(self.semantics)])


if __name__ == '__main__':
    import TeRF.Test.test_grammars as tg
    trs = TypedTRS(tg.types,
                   tg.primitives,
                   tg.semantics)
    print trs
