import pytest

def test_pg_api_select_bob(orb, pg_sql, pg_db, User):
    record = User.select(where=orb.Query('username') == 'bob').first()
    assert record is not None and record.get('username') == 'bob'

def test_pg_api_save_bill(orb, pg_db, User):
    user = User({
        'username': 'bill',
        'password': 'T3st1ng!'
    })
    user.save()

    assert user.is_record() == True
    assert user.get('user_type_id') == 1
    assert user.get('user_type.code') == 'basic'

def test_pg_api_fetch_bill(orb, pg_db, User):
    user = User.byUsername('bill')
    assert user is not None
    id = user.id()
    user = User(id)
    assert user is not None
    user = User.fetch(id)
    assert user is not None

def test_pg_api_delete_bill(orb, pg_db, User):
    user = User.byUsername('bill')
    assert user and user.is_record()

    user.delete()
    assert not user.is_record()

    user_again = User.byUsername('bill')
    assert user_again is None

def test_pg_api_update_bob(orb, pg_sql, pg_db, User):
    record = User.select(where=orb.Query('username') == 'bob').first()

    assert record is not None
    assert record.get('username') == 'bob'

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

def test_pg_api_create_admins(orb, pg_db, User, GroupUser, Group):
    user = User.byUsername('bob')
    assert user is not None and user.get('username') == 'bob'

    group = Group.ensure_exists({'name': 'admins'})
    assert group is not None

    group_user = GroupUser.ensure_exists({'group': group, 'user': user})
    assert group_user.is_record() == True

def test_pg_api_get_user_groups(orb, pg_db, User):
    user = User.byUsername('bob')
    assert user is not None

    groups = user.get('groups')
    import pprint
    pprint.pprint(groups.context().where.__json__())
    assert len(groups) == 1

def test_pg_api_get_group_users(orb, pg_db, Group):
    grp = Group.select(where=orb.Query('name') == 'admins').first()
    assert grp is not None and grp.get('name') == 'admins'

    users = grp.get('users')
    assert len(users) == 1
    assert users[0].get('username') == 'bob'

def test_pg_api_get_group_users_reverse(orb, pg_db, User, Group):
    bob = User.byUsername('bob')
    assert len(bob.get('userGroups')) == 1

    admins = Group.byName('admins')
    assert len(admins.get('groupUsers')) == 1

def test_pg_api_get_group_users_by_unique_index(orb, pg_db, GroupUser, User, Group):
    u = User.byUsername('bob')
    g = Group.byName('admins')

    admin = GroupUser.byUserAndGroup(u, g)
    assert admin is not None

def test_pg_api_get_group_users_by_index(orb, pg_db, GroupUser, User):
    u = User.byUsername('bob')
    users = GroupUser.byUser(u)
    u2 = users[0].get('user')

    assert len(users) == 1
    assert type(u2) == type(u)
    assert u2.id() == u.id()
    assert not u2.is_modified()
    assert not u.is_modified()
    assert u2 == u

def test_pg_api_select_with_join(orb, pg_db, Group, User, GroupUser):
    q  = orb.Query('id') == orb.Query(GroupUser, 'user')
    q &= orb.Query(GroupUser, 'group') == orb.Query(Group, 'id')
    q &= orb.Query(Group, 'name') == 'admins'

    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].get('username') == 'bob'

def test_pg_api_select_standard_with_shortcut(orb, pg_db, GroupUser):
    q = orb.Query('group.name') == 'admins'
    records = GroupUser.select(where=q)

    assert len(records) == 1
    assert records[0].get('user.username') == 'bob'

def test_pg_api_select_reverse_with_shortcut(orb, pg_db, User):
    q = orb.Query('userGroups.group.name') == 'admins'
    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].get('username') == 'bob'

def test_pg_api_select_pipe_with_shortcut(orb, pg_db, User):
    q = orb.Query('groups.name') == 'admins'
    records = User.select(where=q)

    assert len(records) == 1
    assert records[0].get('username') == 'bob'

def test_pg_api_expand(orb, pg_db, GroupUser):
    group_user = GroupUser.select(expand='user').first()
    assert group_user is not None

def test_pg_api_expand_pipe(orb, pg_db, User):
    groups = User.byUsername('bob', expand='groups').get('groups')
    assert len(groups) == 1

    for group in groups:
        assert group.id() is not None

def test_pg_api_expand_lookup(orb, pg_db, User):
    userGroups = User.byUsername('bob', expand='userGroups').get('userGroups')
    assert len(userGroups) == 1

    for userGroup in userGroups:
        assert userGroup.get('user_id') is not None

def test_pg_api_expand_json(orb, pg_db, GroupUser):
    group_user = GroupUser.select(expand='user').first()
    jdata = group_user.__json__()
    assert jdata['user_id'] == jdata['user']['id']

def test_pg_api_expand_complex_json(orb, pg_db, User):
    user = User.byUsername('bob', expand='groups,userGroups,userGroups.group')
    jdata = user.__json__()

    import pprint
    pprint.pprint(jdata)

    assert jdata['groups'][0]['name'] == 'admins'
    assert jdata['userGroups'][0]['user_id'] == jdata['id']
    assert jdata['userGroups'][0]['group']['name'] == 'admins'

def test_pg_api_collection_insert(orb, pg_db, Group):
    records = orb.Collection((Group({'name': 'Test A'}), Group({'name': 'Test B'})))
    records.save()

    assert records[0].id() is not None
    assert records[1].id() is not None

    test_a = Group.byName('Test A')
    test_b = Group.byName('Test B')

    assert records[0].id() == test_a.id()
    assert records[1].id() == test_b.id()

def test_pg_api_collection_delete(orb, pg_db, Group):
    records = Group.select(where=orb.Query('name').in_(('Test A', 'Test B')))

    assert len(records) == 2
    assert records.delete() == 2

def test_pg_api_collection_delete_empty(orb, pg_db, User):
    users = User.select(where=orb.Query('username') == 'missing')
    assert users.delete() == 0

def test_pg_api_collection_has_record(orb, pg_db, User):
    users = User.all()
    assert users.has(User.byUsername('bob'))

def test_pg_api_collection_iter(orb, pg_db, User):
    records = User.select()
    for record in records:
        assert record.is_record()

def test_pg_api_collection_invalid_index(orb, pg_db, User):
    records = User.select()
    with pytest.raises(IndexError):
        records[50]

def test_pg_api_collection_ids(orb, pg_db, User):
    records = User.select().records(order='+id')
    ids = User.select().ids(order='+id')
    for i, record in enumerate(records):
        assert record.id() == ids[i]

def test_pg_api_collection_index(orb, pg_db, User):
    users = User.select()
    urecords = users.records()
    assert users.index(urecords[0]) == 0
    with pytest.raises(ValueError):
        assert users.index(None)

    with pytest.raises(ValueError):
        assert users.index(User())

    with pytest.raises(ValueError):
        assert User.select().index(User())

def test_pg_api_collection_loaded(orb, pg_db, User):
    users = orb.Collection(model=User)
    assert not users.isLoaded()
    assert not users.is_null()

    null_users = orb.Collection()
    assert null_users.is_null()

def test_pg_api_collection_empty(orb, pg_db, User):
    users = orb.Collection()
    assert users.is_empty()

    users = User.select(where=orb.Query('username') == 'billy')
    assert users.is_empty()

def test_pg_api_collection_itertool(orb, pg_db, User):
    for user in User.select(returning='data'):
        assert user['id'] is not None

def test_pg_api_select_columns(orb, pg_db, User):
    data = User.select(columns='username', returning='values').records()
    assert type(data) == list
    assert 'bob' in data
    assert 'sally' in data

def test_pg_api_select_colunms_json(orb, pg_db, User):
    data = User.select(columns='username', returning='values').__json__()
    assert type(data) == list
    assert 'bob' in data
    assert 'sally' in data

def test_pg_api_select_multiple_columns(orb, pg_db, User):
    data = list(User.select(columns=['id', 'username'], returning='values'))
    assert type(data) == list
    assert type(data[0]) == tuple
    assert (1, 'bob') in data

def test_pg_api_save_multi_i18n(orb, pg_db, Document):
    doc = Document()

    with orb.Context(locale='en_US'):
        assert doc.context().locale == 'en_US'
        doc.save({'title': 'Fast'})

    with orb.Context(locale='es_ES'):
        assert doc.context().locale == 'es_ES'
        doc.set('title', 'Rapido')
        doc.save()

def test_pg_api_load_multi_i18n(orb, pg_db, Document):
    with orb.Context(locale='en_US'):
        doc_en = Document.select().last()

    with orb.Context(locale='es_ES'):
        doc_sp = Document.select(locale='es_ES').last()

    assert doc_en.get('title') == 'Fast'
    assert doc_sp.get('title') == 'Rapido'
    assert doc_en.id() == doc_sp.id()

def test_pg_api_load_multi_i18n_with_search(orb, pg_db, Document):
    with orb.Context(locale='en_US'):
        docs_en = Document.select(where=orb.Query('title') == 'Fast')

    with orb.Context(locale='es_ES'):
        docs_sp = Document.select(where=orb.Query('title') == 'Rapido')

    assert len(docs_en) == len(docs_sp)
    assert docs_en[0].get('title') == 'Fast'
    assert docs_sp[0].get('title') == 'Rapido'
    assert len(set(docs_sp.values('id')).difference(docs_en.values('id'))) == 0

def test_pg_api_invalid_reference(orb, pg_db, Employee, User):
    user = User()
    employee = Employee()
    with pytest.raises(orb.errors.InvalidReference):
        employee.set('role', user)
        employee.validate(columns=['role'])

def test_pg_api_save_employee(orb, pg_db, Employee, Role):
    role = Role.ensure_exists({'name': 'Programmer'})
    sam = Employee.byUsername('samantha')
    if not sam:
        sam = Employee({
            'username': 'samantha',
            'password': 'T3st1ng!',
            'role': role
        })
        sam.save()

    assert sam.get('username') == 'samantha'
    assert sam.get('role') == role

def test_pg_api_save_hash_id(orb, pg_db, Comment):
    comment = Comment({'text': 'Testing'})
    comment.save()
    assert isinstance(comment.id(), unicode)

def test_pg_api_restore_hash_id(orb, pg_db, Comment):
    comment = Comment.select().last()
    assert isinstance(comment.id(), unicode)

def test_pg_api_reference_hash_id(orb, pg_db, Comment, Attachment):
    comment = Comment.select().last()
    attachment = Attachment({'filename': '/path/to/somewhere', 'comment': comment})
    attachment.save()

    assert isinstance(attachment.get('comment_id'), unicode)

def test_pg_api_reference_auto_expanding(orb, pg_db, Comment, Employee):
    comment = Comment.select().last()
    user = Employee.select().last()

    # ensure default collector expands work
    comment_json = comment.__json__()
    assert 'attachments' in comment_json
    assert len(comment_json['attachments']) > 0

    # ensure default user expands work
    user_json = user.__json__()

    import pprint
    pprint.pprint(user_json)

    assert 'role' in user_json
    assert user_json['role']['id'] is not None

def test_pg_expand_virtual(orb, pg_db, GroupUser, User):
    gu = GroupUser.select().first().get('user')
    u = User.select(where=orb.Query('id') == gu, expand='my_groups.users,groups.users').first()
    json = u.__json__()
    import pprint
    pprint.pprint(json)
    assert len(json['groups']) == len(json['my_groups'])
    assert len(json['groups'][0]['users']) == len(json['my_groups'][0]['users'])

def test_pg_sub_selection(orb, pg_db, GroupUser, User):
    a = orb.Query('user').in_(User.select())
    b = orb.Query('user').in_(User.select(columns=['id']))
    c = orb.Query('user.username').in_(User.select(columns=['username']))

    assert len(GroupUser.select()) != 0
    assert len(GroupUser.select()) == len(GroupUser.select(where=a))
    assert len(GroupUser.select()) == len(GroupUser.select(where=b))
    assert len(GroupUser.select()) == len(GroupUser.select(where=c))

def test_read_write_servers(orb, pg_db, Comment):
    db = orb.system.database()

    read_host = 'localhost'
    write_host = '127.0.0.1'

    # connect to different read/write servers
    db.set_host(read_host)
    db.set_write_host(write_host)

    conn = db.connection()
    orig_open = conn.open

    def new_open(writeAccess=False):
        # make sure the operation is performing the proper
        # level of access
        assert new_open.read != writeAccess

        # create a new connection
        out = orig_open(writeAccess=writeAccess)
        hosts = conn._SQLConnection__pool.keys()
        if writeAccess:
            assert write_host in hosts
        else:
            assert read_host in hosts
        return out

    setattr(new_open, 'read', False)
    conn.open = new_open

    # test read
    new_open.read = True
    comment = Comment.select().first()
    assert comment is not None

    # test update
    new_open.read = False
    comment.set('text', 'some new text')
    comment.save()

    # test create
    comment = Comment({'text': 'New comment'})
    assert comment.id() is None
    comment.save()
    assert comment.id() is not None

    # test delete
    assert comment.delete() == 1

    # reset the open command
    conn.open = orig_open

def test_null_query(orb, pg_db, Comment):
    assert len(Comment.select(where=orb.Query('id').in_([]))) == 0
    assert len(Comment.select(where=orb.Query('id').notIn([]))) == len(Comment.select())