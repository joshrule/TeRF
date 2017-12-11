import TeRF.Types.Type as Type


class TypeBinding(Type.Type):
    """
    an abstraction binding a variable appearing in some body type

    Parameters
    ----------
    variable: TeRF.Types.TypeVariable
        the variable being bound
    body: TeRF.Types.Type
        the type over which the binding has scope
    """
    def __init__(self, variable, body):
        self.variable = variable
        self.body = body

    def __eq__(self, other):
        """**doesn't** consider equality up to renaming!"""
        try:
            return self.variable == other.variable and self.body == other.body
        except AttributeError:
            return False

    def __hash__(self):
        return hash((self.variable, self.body))

    def __repr__(self):
        return 'TypeBinding(variable={!r}, body={!r})'.format(self.variable,
                                                              self.body)

    def __str__(self):
        return '()' + str(self.variable) + '.' + str(self.body)


TBind = TypeBinding
