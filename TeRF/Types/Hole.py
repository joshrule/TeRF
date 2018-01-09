import TeRF.Types.Variable as Var


class Hole(Var.Var):
    """a gap in a term"""
    def __init__(self, **kwargs):
        super(Hole, self).__init__(**kwargs)
        self.name = str(self.identity)

    def __repr__(self):
        return 'Hole(identity={})'.format(self.identity)

    def __str__(self):
        return '_' + self.name + '_'
