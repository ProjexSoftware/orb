from projex.lazymodule import lazy_import
from ..sqliteconnection import SQLiteStatement

orb = lazy_import('orb')


class ADD_COLUMN(SQLiteStatement):
    def __call__(self, column):
        # determine all the flags for this column
        flags = []
        Flags = orb.Column.Flags
        for key, value in Flags.items():
            if column.flags() & value:
                flag_sql = SQLiteStatement.byName('Flag::{0}'.format(key))
                if flag_sql:
                    flags.append(flag_sql)

        return 'ADD COLUMN "{0}" {1} {2}'.format(column.field(), column.dbType('Postgres'), ' '.join(flags)).strip()


SQLiteStatement.registerAddon('ADD COLUMN', ADD_COLUMN())
