def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'You are not logged in.' in response.data
