import os
import tempfile

import pytest

from main import app, db


@pytest.fixture
def client():
    app.config['TESTING'] = True
    client = app.test_client()
    transaction = db.session.begin_nested()
    
    yield client

    transaction.rollback()
   

