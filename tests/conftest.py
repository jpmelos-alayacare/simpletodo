import os
import tempfile

import pytest

from app import app, init_db


@pytest.fixture
def client():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
    app.config['TESTING'] = True
    client = app.test_client()

    with app.app_context():
        init_db()

    return client
