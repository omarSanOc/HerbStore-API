import os
from pathlib import Path

os.environ.setdefault("DATABASE_URL", "sqlite+pysqlite:///./pytest.db")
os.environ.setdefault("ORDER_PROCESSING_MS", "50")

DATABASE_FILE = Path("pytest.db")
DATABASE_FILE.unlink(missing_ok=True)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402
from scripts.seed import seed  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def database():
    Base.metadata.create_all(engine)
    assert seed() == 300
    yield
    engine.dispose()
    DATABASE_FILE.unlink(missing_ok=True)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def valid_order():
    return {
        "items": [{"productId": "product-261009-043", "quantity": 2}],
        "shippingAddress": {
            "fullName": "Test Customer",
            "phone": "5512345678",
            "postalCode": "03100",
            "state": "CDMX",
            "city": "Benito Juárez",
            "street": "Fictional Avenue",
            "exteriorNumber": "42",
        },
        "currency": "MXN",
    }
