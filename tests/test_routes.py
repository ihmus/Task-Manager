def test_home_page(auth_client):
    """'/new-note' rotasını test eder."""
    response = auth_client.get('/new-note')
    assert response.status_code == 200

def test_users_list_page(auth_client):
    """'/users' rotasını test eder."""
    response = auth_client.get('/users')
    assert response.status_code == 200

def test_gorevler_page(auth_client):
    """'/gorevler' rotasını test eder."""
    response = auth_client.get('/gorevler')
    assert response.status_code == 200