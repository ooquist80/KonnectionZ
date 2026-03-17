def test_healthcheck(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_list_and_get_user(client):
    create_response = client.post(
        "/users",
        json={"email": "ada@example.com", "full_name": "Ada Lovelace"},
    )

    assert create_response.status_code == 201
    created_user = create_response.json()

    list_response = client.get("/users")
    assert list_response.status_code == 200
    assert list_response.json() == [created_user]

    get_response = client.get(f"/users/{created_user['id']}")
    assert get_response.status_code == 200
    assert get_response.json() == created_user


def test_duplicate_email_returns_conflict(client):
    payload = {"email": "ada@example.com", "full_name": "Ada Lovelace"}

    first_response = client.post("/users", json=payload)
    second_response = client.post("/users", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
