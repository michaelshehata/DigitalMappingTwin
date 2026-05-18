from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

def test_predict():

    response = client.post(
        "/predict"
    )

    assert response.status_code == 200

    data = response.json()

    assert "geojson" in data

    assert (
        "predicted_change_percentage"
        in data
    )