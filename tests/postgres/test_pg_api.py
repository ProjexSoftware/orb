import pytest

from test_marks import requires_pg


@requires_pg
def test_pg_api_select_bob(orb, pg_sql, pg_db, User):
    record = User.select(where=orb.Query('username') == 'bob').first()
    assert record is not None and record.get('username') == 'bob'

@requires_pg
def test_pg_api_save_bill(orb, pg_db, User):
    user = User({
        'username': 'bill',
        'password': 'T3st1ng!'
    })
    user.save()

    assert user.isRecord() == True

@requires_pg
def test_pg_api_fetch_bill(orb, pg_db, User):
    user = User.byUsername('bill')
    assert user is not None
    id = user.id()
    user = User(id)
    assert user is not None
    user = User.fetch(id)
    assert user is not None

@requires_pg
def test_pg_api_delete_bill(orb, pg_db, User):
    user = User.byUsername('bill')
    assert user and user.isRecord()

    user.delete()
    assert not user.isRecord()

    user_again = User.byUsername('bill')
    assert user_again is None

@requires_pg
def test_pg_api_update_bob(orb, pg_sql, pg_db, User):
    record = User.select(where=orb.Query('username') == 'bob').first()

    assert record is not None
    assert record.username() == 'bob'

    st = pg_sql.statement('UPDATE')
    conn = pg_db.connection()

    # set to tim
    record.set('username', 'tim')
    sql, data = st([record])
    result, count = conn.execute(sql, data)

    record_tim = User.select(where=orb.Query('username') == 'tim').first()
    assert record_tim is not None
    assert record_tim.id() == record.id()

    # set back to bob
    record_tim.set('username', 'bob')
    sql, data = st([record_tim])
    result, count = conn.execute(sql, data)

    record_bob = User.select(where=orb.Query('username') == 'bob').first()
    assert record_bob is not None
    assert record_bob.id() == record.id() and record_bob.id() == record_tim.id()

@requires_pg
def test_pg_api_create_admins(orb, User, GroupUser, Group):
    user = User.byUsername('bob')
    assert user is not None and user.username() == 'bob'

    group = Group.ensureExists({'name': 'admins'})
    assert group is not None

    group_user = GroupUser.ensureExists({'group': group, 'user': user})
    assert group_user.isRecord() == True

@requires_pg
def test_pg_api_get_user_groups(orb, User):
    user = User.byUsername('bob')
    assert user is not None

    groups = user.groups()
    assert len(groups) == 1

@requires_pg
def test_pg_api_get_group_users(orb, Group):
    grp = Group.select(where=orb.Query('name') == 'admins').first()
    assert grp is not None and grp.name() == 'admins'

    users = grp.users()
    assert len(users) == 1
    assert users[0].username() == 'bob'

@requires_pg
def test_pg_api_get_group_users_reverse(orb, User, Group):
    bob = User.byUsername('bob')
    assert len(bob.userGroups()) == 1

    admins = Group.byName('admins')
    assert len(admins.groupUsers()) == 1

@requires_pg
def test_pg_api_get_group_users_by_unique_index(orb, GroupUser, User, Group):
    u = User.byUsername('bob')
    g = Group.byName('admins')

    admin = GroupUser.byUserAndGroup(u, g)
    assert admin is not None

@requires_pg
def test_pg_api_get_group_users_by_index(orb, GroupUser, User):
    u = User.byUsername('bob')
    users = GroupUser.byUser(u)
    assert len(users) == 1
    assert users[0].user() == u

@requires_pg
def test_pg_api_select_with_join(orb, Group, User, GroupUser):
    q  = orb.Query('id') == orb.Query(GroupUser, 'user')
    q &= orb.Query(GroupUser, 'group') == orb.Query(Group, 'id')
    q &= orb.Query(Group, 'name') == 'admins'

    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].username() == 'bob'

@requires_pg
def test_pg_api_select_standard_with_shortcut(orb, GroupUser):
    q = orb.Query('group.name') == 'admins'
    records = GroupUser.select(where=q)

    assert len(records) == 1
    assert records[0].user().username() == 'bob'

@requires_pg
def test_pg_api_select_reverse_with_shortcut(orb, User):
    q = orb.Query('userGroups.group.name') == 'admins'
    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].username() == 'bob'

@requires_pg
def test_pg_api_select_pipe_with_shortcut(orb, User):
    q = orb.Query('groups.name') == 'admins'
    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].username() == 'bob'

@requires_pg
def test_pg_api_expand(orb, GroupUser):
    group_user = GroupUser.select(expand='user').first()
    assert group_user is not None

@requires_pg
def test_pg_api_expand_pipe(orb, User):
    groups = User.byUsername('bob', expand='groups').groups()
    assert len(groups) == 1

    for group in groups:
        assert group.id() is not None

@requires_pg
def test_pg_api_expand_lookup(orb, User):
    userGroups = User.byUsername('bob', expand='userGroups').userGroups()
    assert len(userGroups) == 1

    for userGroup in userGroups:
        assert userGroup.get('user_id') is not None

@requires_pg
def test_pg_api_expand_json(orb, GroupUser):
    group_user = GroupUser.select(expand='user').first()
    jdata = group_user.__json__()
    assert jdata['user_id'] == jdata['user']['id']

@requires_pg
def test_pg_api_expand_complex_json(orb, User):
    user = User.byUsername('bob', expand='groups,userGroups,userGroups.group')
    jdata = user.__json__()

    assert jdata['groups'][0]['name'] == 'admins'
    assert jdata['userGroups'][0]['user_id'] == jdata['id']
    assert jdata['userGroups'][0]['group']['name'] == 'admins'

@requires_pg
def test_pg_api_collection_insert(orb, Group):
    records = orb.Collection((Group({'name': 'Test A'}), Group({'name': 'Test B'})))
    records.save()

    assert records[0].id() is not None
    assert records[1].id() is not None

    test_a = Group.byName('Test A')
    test_b = Group.byName('Test B')

    assert records[0].id() == test_a.id()
    assert records[1].id() == test_b.id()

@requires_pg
def test_pg_api_collection_delete(orb, Group):
    records = Group.select(where=orb.Query('name').in_(('Test A', 'Test B')))

    assert len(records) == 2
    assert records.delete() == 2

@requires_pg
def test_pg_api_collection_delete_empty(orb, User):
    users = User.select(where=orb.Query('username') == 'missing')
    assert users.delete() == 0

@requires_pg
def test_pg_api_collection_has_record(orb, User):
    users = User.all()
    assert users.has(User.byUsername('bob'))

@requires_pg
def test_pg_api_collection_iter(orb, User):
    records = User.select()
    for record in records:
        assert record.isRecord()

@requires_pg
def test_pg_api_collection_invalid_index(orb, User):
    records = User.select()
    with pytest.raises(IndexError):
        records[50]

@requires_pg
def test_pg_api_collection_ids(orb, User):
    records = User.select().records(order='+id')
    ids = User.select().ids(order='+id')
    for i, record in enumerate(records):
        assert record.id() == ids[i]

@requires_pg
def test_pg_api_collection_index(orb, User):
    users = User.select()
    urecords = users.records()
    assert users.index(urecords[0]) == 0
    assert users.index(None) == -1

    with pytest.raises(ValueError):
        assert users.index(User()) == -1

    with pytest.raises(ValueError):
        assert User.select().index(User())

@requires_pg
def test_pg_api_collection_loaded(orb, User):
    users = orb.Collection(model=User)
    assert not users.isLoaded()
    assert not users.isNull()

    null_users = orb.Collection()
    assert null_users.isNull()

@requires_pg
def test_pg_api_collection_empty(orb, User):
    users = orb.Collection()
    assert users.isEmpty()

    users = User.select(where=orb.Query('username') == 'billy')
    assert users.isEmpty()

@requires_pg
def test_pg_api_collection_itertool(orb, User):
    for user in User.select(inflated=False):
        assert user['id'] is not None

@requires_pg
def test_pg_api_select_columns(orb, User):
    data = User.select(columns='username', returning='values').records()
    assert type(data) == list
    assert 'bob' in data
    assert 'sally' in data

@requires_pg
def test_pg_api_select_colunms_json(orb, User):
    data = User.select(columns='username', returning='values').__json__()
    assert type(data) == list
    assert 'bob' in data
    assert 'sally' in data

@requires_pg
def test_pg_api_select_multiple_columns(orb, User):
    data = list(User.select(columns=['id', 'username'], returning='values'))
    assert type(data) == list
    assert type(data[0]) == tuple
    assert (1, 'bob') in data

@requires_pg
def test_pg_api_save_multi_i18n(orb, Document):
    doc = Document()

    with orb.Context(locale='en_US'):
        assert doc.context().locale == 'en_US'
        doc.save({'title': 'Fast'})

    with orb.Context(locale='es_ES'):
        assert doc.context().locale == 'es_ES'
        doc.set('title', 'Rapido')
        doc.save()

@requires_pg
def test_pg_api_load_multi_i18n(orb, Document):
    with orb.Context(locale='en_US'):
        doc_en = Document.select().last()

    with orb.Context(locale='es_ES'):
        doc_sp = Document.select(locale='es_ES').last()

    assert doc_en.title() == 'Fast'
    assert doc_sp.title() == 'Rapido'
    assert doc_en.id() == doc_sp.id()

@requires_pg
def test_pg_api_load_multi_i18n_with_search(orb, Document):
    with orb.Context(locale='en_US'):
        docs_en = Document.select(where=orb.Query('title') == 'Fast')

    with orb.Context(locale='es_ES'):
        docs_sp = Document.select(where=orb.Query('title') == 'Rapido')

    assert len(docs_en) == len(docs_sp)
    assert docs_en[0].title() == 'Fast'
    assert docs_sp[0].title() == 'Rapido'
    assert len(set(docs_sp.values('id')).difference(docs_en.values('id'))) == 0

@requires_pg
def test_pg_api_invalid_reference(orb, Employee, User):
    user = User()
    employee = Employee()
    with pytest.raises(orb.errors.InvalidReference):
        employee.setRole(user)

@requires_pg
def test_pg_api_save_employee(orb, Employee, Role):
    role = Role.ensureExists({'name': 'Programmer'})
    sam = Employee.byUsername('samantha')
    if not sam:
        sam = Employee({
            'username': 'samantha',
            'password': 'T3st1ng!',
            'role': role
        })
        sam.save()

    assert sam.username() == 'samantha'
    assert sam.role() == role

@requires_pg
def test_pg_api_save_hash_id(orb, Comment):
    comment = Comment({'text': 'Testing'})
    comment.save()
    assert isinstance(comment.id(), str)

@requires_pg
def test_pg_api_restore_hash_id(orb, Comment):
    comment = Comment.select().last()
    assert isinstance(comment.id(), str)

@requires_pg
def test_pg_api_reference_hash_id(orb, Comment, Attachment):
    comment = Comment.select().last()
    attachment = Attachment({'filename': '/path/to/somewhere', 'comment': comment})
    attachment.save()

    assert isinstance(attachment.get('comment_id'), str)

@requires_pg
def test_pg_expand_virtual(orb, GroupUser, User):
    gu = GroupUser.select().first().user()
    u = User.select(where=orb.Query('id') == gu, expand='my_groups.users,groups.users').first()
    json = u.__json__()
    assert len(json['groups']) == len(json['my_groups'])
    assert len(json['groups'][0]['users']) == len(json['my_groups'][0]['users'])

@requires_pg
def test_pg_extract_values(orb, TestAllColumns, GroupUser, Group):
    import datetime
    users = GroupUser.all()
    all_records = TestAllColumns.all()

    assert isinstance(all_records.values('date')[0], datetime.date)
    assert isinstance(all_records.values('datetime')[0], datetime.datetime)
    assert isinstance(users.values('group')[0], Group)
    assert not isinstance(users.values('group_id')[0], Group)

    group, group_id = users.values('group', 'group_id')[0]
    assert isinstance(group, Group)
    assert not isinstance(group_id, Group)