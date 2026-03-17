def test_create_list_get_update_and_delete_wordset(client):
    create_response = client.post(
        "/wordsets",
        json={
            "category": "Animals",
            "difficulty": 1,
            "words": ["cat", "dog", "mouse", "horse"],
        },
    )

    assert create_response.status_code == 201
    created_wordset = create_response.json()
    assert created_wordset == {
        "id": 1,
        "category": "Animals",
        "difficulty": 1,
        "words": ["cat", "dog", "mouse", "horse"],
    }

    list_response = client.get("/wordsets")
    assert list_response.status_code == 200
    assert list_response.json() == [created_wordset]

    get_response = client.get("/wordsets/1")
    assert get_response.status_code == 200
    assert get_response.json() == created_wordset

    update_response = client.put(
        "/wordsets/1",
        json={
            "category": "Advanced Animals",
            "difficulty": 2,
            "words": ["tiger", "lion", "panther", "leopard"],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json() == {
        "id": 1,
        "category": "Advanced Animals",
        "difficulty": 2,
        "words": ["tiger", "lion", "panther", "leopard"],
    }

    delete_response = client.delete("/wordsets/1")
    assert delete_response.status_code == 204
    assert delete_response.content == b""

    missing_response = client.get("/wordsets/1")
    assert missing_response.status_code == 404


def test_wordset_invalid_difficulty_returns_bad_request(client):
    response = client.post(
        "/wordsets",
        json={
            "category": "Impossible",
            "difficulty": 99,
            "words": ["one", "two", "three", "four"],
        },
    )

    assert response.status_code == 400


def test_wordset_requires_at_least_four_words(client):
    response = client.post(
        "/wordsets",
        json={"category": "Tiny", "difficulty": 1, "words": ["one", "two", "three"]},
    )

    assert response.status_code == 422


def test_updating_missing_wordset_returns_not_found(client):
    response = client.put(
        "/wordsets/999",
        json={
            "category": "Missing",
            "difficulty": 1,
            "words": ["alpha", "beta", "gamma", "delta"],
        },
    )

    assert response.status_code == 404
