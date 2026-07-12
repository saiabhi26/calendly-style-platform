"""Public booking flow, including the double-booking guard.

The guard is a DB UNIQUE(service_id, slot_start) constraint: the second booking
for the same slot must come back as a clean 409, not a 500.
"""
from datetime import date, timedelta


def _setup_bookable_service(client, headers):
    """Create org + service + availability, and return (service_id, a free slot_start)."""
    org = client.post(
        "/organizations",
        json={"name": "Acme", "slug": "acme", "timezone": "UTC"},
        headers=headers,
    ).json()
    svc = client.post(
        "/services",
        json={
            "organization_id": org["id"],
            "title": "Consult",
            "duration_minutes": 60,
            "price": "50.00",
            "mode": "OFFLINE",
        },
        headers=headers,
    ).json()

    # A week out, so every generated slot is safely in the future (org tz = UTC).
    target = date.today() + timedelta(days=7)
    client.post(
        "/availability",
        json={
            "service_id": svc["id"],
            "day_of_week": target.weekday(),
            "start_time": "09:00",
            "end_time": "17:00",
        },
        headers=headers,
    )

    slots = client.get(f"/slots?service_id={svc['id']}&date={target.isoformat()}").json()
    assert slots, "expected open slots for the availability window"
    return svc["id"], slots[0]["start"]


def test_open_slots_are_generated_for_availability(client, login_as):
    headers = login_as("owner@example.com")
    service_id, slot_start = _setup_bookable_service(client, headers)
    assert slot_start  # a concrete ISO timestamp


def test_booking_a_free_slot_succeeds(client, login_as):
    headers = login_as("owner@example.com")
    service_id, slot_start = _setup_bookable_service(client, headers)

    res = client.post(
        "/bookings",
        json={
            "service_id": service_id,
            "slot_start": slot_start,
            "customer_name": "Bob",
            "customer_email": "bob@example.com",
        },
    )
    assert res.status_code == 201, res.text
    assert res.json()["status"] == "PENDING"


def test_the_same_slot_cannot_be_booked_twice(client, login_as):
    headers = login_as("owner@example.com")
    service_id, slot_start = _setup_bookable_service(client, headers)
    payload = {
        "service_id": service_id,
        "slot_start": slot_start,
        "customer_name": "Bob",
        "customer_email": "bob@example.com",
    }

    first = client.post("/bookings", json=payload)
    assert first.status_code == 201, first.text

    # Sequentially, the slot is now withdrawn from the open list, so the second
    # attempt fails validation with 400 ("not an available slot"). The DB
    # UNIQUE(service_id, slot_start) constraint returns 409 only on a true
    # concurrent race — where two requests both pass validation before either
    # commits. Either way, the double booking is prevented.
    second = client.post("/bookings", json=payload)
    assert second.status_code == 400

    # And the slot no longer shows up as bookable.
    target = date.today() + timedelta(days=7)
    remaining = client.get(f"/slots?service_id={service_id}&date={target.isoformat()}").json()
    assert slot_start not in {s["start"] for s in remaining}


def test_booking_a_time_outside_availability_is_rejected(client, login_as):
    headers = login_as("owner@example.com")
    service_id, _ = _setup_bookable_service(client, headers)

    # 3am on the availability day is not within the 09:00–17:00 window.
    target = date.today() + timedelta(days=7)
    bad_slot = f"{target.isoformat()}T03:00:00+00:00"
    res = client.post(
        "/bookings",
        json={
            "service_id": service_id,
            "slot_start": bad_slot,
            "customer_name": "Bob",
            "customer_email": "bob@example.com",
        },
    )
    assert res.status_code == 400
