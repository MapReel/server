import uuid

import pytest
from httpx import AsyncClient

from tests.conftest import TripFixture


@pytest.mark.asyncio
async def test_create_video_metadata(client: AsyncClient, test_trip: TripFixture):
    body = {
        "capturedAt": "2026-06-02T12:00:00Z",
        "durationMs": 3000,
        "latitude": 37.5665,
        "longitude": 126.978,
        "placeId": "ChIJN1t_tDeuEmsRUsoyG83frY4",
    }
    resp = await client.post(f"/api/v1/trips/{test_trip.id}/videos", json=body)
    assert resp.status_code == 201

    data = resp.json()
    assert data["tripId"] == str(test_trip.id)
    assert data["durationMs"] == 3000
    assert data["latitude"] == 37.5665
    assert data["longitude"] == 126.978
    assert data["placeId"] == "ChIJN1t_tDeuEmsRUsoyG83frY4"
    assert "id" in data
    assert "createdAt" in data
    assert "updatedAt" in data


@pytest.mark.asyncio
async def test_create_video_for_nonexistent_trip(client: AsyncClient):
    fake_trip_id = uuid.uuid4()
    body = {
        "capturedAt": "2026-06-02T12:00:00Z",
        "durationMs": 3000,
    }
    resp = await client.post(f"/api/v1/trips/{fake_trip_id}/videos", json=body)
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_video_for_other_users_trip(
    client: AsyncClient, other_user_trip: TripFixture
):
    body = {
        "capturedAt": "2026-06-02T12:00:00Z",
        "durationMs": 3000,
    }
    resp = await client.post(f"/api/v1/trips/{other_user_trip.id}/videos", json=body)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_list_videos_returns_created(client: AsyncClient, test_trip: TripFixture):
    body = {
        "capturedAt": "2026-06-02T12:00:00Z",
        "durationMs": 3000,
    }
    create_resp = await client.post(f"/api/v1/trips/{test_trip.id}/videos", json=body)
    assert create_resp.status_code == 201

    list_resp = await client.get(f"/api/v1/trips/{test_trip.id}/videos")
    assert list_resp.status_code == 200

    videos = list_resp.json()
    assert len(videos) == 1
    assert videos[0]["id"] == create_resp.json()["id"]


@pytest.mark.asyncio
async def test_list_videos_empty(client: AsyncClient, test_trip: TripFixture):
    resp = await client.get(f"/api/v1/trips/{test_trip.id}/videos")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_delete_video(client: AsyncClient, test_trip: TripFixture):
    body = {
        "capturedAt": "2026-06-02T12:00:00Z",
        "durationMs": 3000,
    }
    create_resp = await client.post(f"/api/v1/trips/{test_trip.id}/videos", json=body)
    video_id = create_resp.json()["id"]

    del_resp = await client.delete(f"/api/v1/trips/{test_trip.id}/videos/{video_id}")
    assert del_resp.status_code == 204

    list_resp = await client.get(f"/api/v1/trips/{test_trip.id}/videos")
    assert list_resp.json() == []
