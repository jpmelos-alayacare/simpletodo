from app import db, User


def test_login(client):
    # TODO: This should actually be in a fixture.
    user = User(username='test', email='test@test.com', pw_hash=User.hash_password('password'))
    db.session.add(user)
    db.session.commit()

    response = client.post('/login', data={
        'username': 'test',
        'password': 'password',
    })

    assert b'You are logged in!' in response.data
    assert b'Username: test' in response.data
