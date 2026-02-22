"""Shared pytest fixtures."""
import os
import pytest
from sqlalchemy.pool import StaticPool

from app import create_app, db as _db


@pytest.fixture(scope="session")
def app():
    os.makedirs("/tmp/donations_crm_test_uploads", exist_ok=True)
    test_app = create_app(
        {
            "TESTING": True,
            # Use StaticPool so all connections share the same in-memory DB
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SQLALCHEMY_ENGINE_OPTIONS": {
                "connect_args": {"check_same_thread": False},
                "poolclass": StaticPool,
            },
            "WTF_CSRF_ENABLED": False,
            "UPLOAD_FOLDER": "/tmp/donations_crm_test_uploads",
            "SECRET_KEY": "test-secret",
        }
    )
    yield test_app


@pytest.fixture()
def client(app):
    with app.app_context():
        _db.create_all()
        yield app.test_client()
        _db.session.remove()
        _db.drop_all()


@pytest.fixture()
def db(app):
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.remove()
        _db.drop_all()
