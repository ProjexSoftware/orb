from orb.core.column import Column


class JoinColumn(Column):
    def __init__(self, joiner=None, **kwds):
        super(JoinColumn, self).__init__(**kwds)

        # set standard properties
        self.set_flag(Column.Flags.ReadOnly)
        self.set_flag(Column.Flags.Virtual)

        # define custom properties
        self.__joiner = joiner

    def copy(self):
        out = super(JoinColumn, self).copy()
        out.setJoiner(self.joiner())
        return out

    def joiner(self):
        return self.__joiner

    def setJoiner(self, joiner):
        """
        Sets the joiner query for this column to the inputted query.

        :param      query | (<orb.Column>, <orb.Query>) || <callable> || None
        """
        self.__joiner = joiner

