import os
import time

import pytest
import httpx
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base


TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL")

if TEST_DATABASE_URL is None:
    raise RuntimeError("TEST_DATABASE_URL is not set in environment for tests")

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture(scope="session", autouse=True)
def ensure_db_up():
    retries = 20
    while retries:
        try:
            conn = engine.connect()
            conn.close()
            break
        except Exception:
            retries -= 1
            time.sleep(1)
    if retries == 0:
        raise RuntimeError("Database not reachable for tests")


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session():
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client():
    base_url = "http://web:8000"
    for _ in range(20):
        try:
            r = httpx.get(f"{base_url}/")
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)
    else:
        raise RuntimeError("Web service did not start in time")

    with httpx.Client(base_url=base_url, timeout=10.0) as c:
        yield c
