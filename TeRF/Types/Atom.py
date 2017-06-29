class Atom(object):
    def __init__(self, name=None):
        self.identity = object()  # gensym!
        self.name = str(id(self.identity)) if name is None else name
