from projex.lazymodule import lazy_import
from ..mysqlconnection import MySQLStatement

orb = lazy_import('orb')


class ADD_COLUMN(MySQLStatement):
    def __call__(self, column):
        # determine all the flags for this column
        flags = []
        Flags = orb.Column.Flags
        for key, value in Flags:
            if column.flags() & value:
                flag_sql = MySQLStatement.byName('Flag::{0}'.format(key))
                if flag_sql:
                    flags.append(flag_sql)

        engine = column.get_engine('MySQL')
        db_type = engine.get_column_type(column, 'MySQL')

        sql = u'ADD COLUMN `{0}` {1} {2}'.format(column.field(), db_type, ' '.join(flags)).strip()
        return sql, {}


MySQLStatement.registerAddon('ADD COLUMN', ADD_COLUMN())
