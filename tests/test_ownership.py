"""Multi-tenancy: every query is scoped to the authenticated owner, and
cross-tenant access returns 404 (never 403 — we don't leak that the row exists).
"""


def _create_org(client, headers, slug="acme"):
    res = client.post(
        "/organizations",
        json={"name": "Acme", "slug": slug, "timezone": "UTC"},
        headers=headers,
    )
    assert res.status_code == 201, res.text
    return res.json()


def test_org_list_is_scoped_to_the_owner(client, login_as):
    alice = login_as("alice@example.com")
    bob = login_as("bob@example.com")
    _create_org(client, alice, slug="alice-co")

    # Alice sees her org; Bob sees nothing.
    assert len(client.get("/organizations", headers=alice).json()) == 1
    assert client.get("/organizations", headers=bob).json() == []


def test_reading_another_owners_org_returns_404(client, login_as):
    alice = login_as("alice@example.com")
    bob = login_as("bob@example.com")
    org = _create_org(client, alice, slug="alice-co")

    res = client.get(f"/organizations/{org['id']}", headers=bob)
    assert res.status_code == 404


def test_creating_a_service_under_a_foreign_org_returns_404(client, login_as):
    alice = login_as("alice@example.com")
    bob = login_as("bob@example.com")
    org = _create_org(client, alice, slug="alice-co")

    res = client.post(
        "/services",
        json={"organization_id": org["id"], "title": "Consult", "duration_minutes": 60},
        headers=bob,
    )
    assert res.status_code == 404


def test_duplicate_slug_conflicts(client, login_as):
    alice = login_as("alice@example.com")
    _create_org(client, alice, slug="taken")
    res = client.post(
        "/organizations",
        json={"name": "Other", "slug": "taken", "timezone": "UTC"},
        headers=alice,
    )
    assert res.status_code == 409
