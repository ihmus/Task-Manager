def test_create_note_logic(auth_client):
    """'/create_note' rotasına veri gönderimini test eder."""
    data = {
        'title': 'Test Görevi',
        'description': 'Açıklama',
        'category_id': '1', # conftest'teki kategorinin ID'si
        'start_date': '2023-12-01T10:00',
        'deadline': '2023-12-10T10:00'
    }
    # views.py'deki gerçek rota /create_note
    response = auth_client.post('/create_note', data=data, follow_redirects=True)
    assert response.status_code == 200
    assert b"Test" in response.data