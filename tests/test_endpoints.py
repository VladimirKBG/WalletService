from uuid import uuid4
from decimal import Decimal

from app.models.wallet import Wallet


def test_deposit_and_withdraw_flow(db_session, client):
    wallet_id = uuid4()
    w = Wallet(id=wallet_id, balance=Decimal("0.00"))
    db_session.add(w)
    db_session.commit()

    payload = {"operation_type": "DEPOSIT", "amount": 100.00}
    r = client.post(f"/api/v1/wallets/{wallet_id}/operation", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["wallet_id"] == str(wallet_id)
    assert Decimal(data["amount"]) == 100.0

    r2 = client.get(f"/api/v1/wallets/{wallet_id}")
    assert r2.status_code == 200, r2.text
    wdata = r2.json()
    assert Decimal(wdata["balance"]) == 100.0

    r3 = client.post(f"/api/v1/wallets/{wallet_id}/operation", json={"operation_type": "WITHDRAW", "amount": 30.00})
    assert r3.status_code == 201
    r4 = client.get(f"/api/v1/wallets/{wallet_id}")
    assert Decimal(r4.json()["balance"]) == 70.0

    r5 = client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 100.00},
    )
    assert r5.status_code == 400, r5.text
    err = r5.json()
    assert "insufficient" in err["detail"].lower()
    r6 = client.get(f"/api/v1/wallets/{wallet_id}")
    assert float(r6.json()["balance"]) == 70.0
