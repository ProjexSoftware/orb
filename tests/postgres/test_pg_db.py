import pytest
from test_marks import requires_pg


@pytest.mark.run(order=1)
@requires_pg
def test_pg_loaded(orb):
    from orb.core.connection_types.sql.postgres import PSQLConnection
    assert orb.Connection.byName('Postgres') == PSQLConnection

@pytest.mark.run(order=1)
@requires_pg
def test_pg_db_connection(pg_db):
    assert pg_db.connect() is not None

@pytest.mark.run(order=1)
@requires_pg
def test_pg_db_sync(orb, pg_db, testing_schema):
    pg_db.sync()