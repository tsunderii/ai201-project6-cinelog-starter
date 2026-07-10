"""
tests/test_watchlist.py — CineLog (feature/watchlist branch)

Tests for the watchlist service. These follow the same fixture and
assertion structure as tests/test_collection.py — in particular,
test_add_to_watchlist_nonexistent_film_raises is modeled directly on
test_add_to_collection_nonexistent_film_raises.
"""

import pytest
from app import create_app, db
from models import User, Film
from services.watchlist_service import add_to_watchlist
from services.collection_service import FilmNotFoundError


@pytest.fixture
def app():
    """Create an isolated test app with an in-memory database."""
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    """A user to use in tests."""
    with app.app_context():
        user = User(username="testuser", email="test@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    """A film to use in tests."""
    with app.app_context():
        film = Film(title="Paddington 2", year=2017, genre="Comedy")
        db.session.add(film)
        db.session.commit()
        return film.id


# ── Nonexistent film ─────────────────────────────────────────────────────────

def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    """
    Adding a film_id that doesn't exist in the database should raise
    FilmNotFoundError, not a database integrity error.

    Modeled on test_add_to_collection_nonexistent_film_raises. On this
    (pre-refactor) branch Film IDs are integers, so a clearly-unused
    integer id stands in for a missing film. Comment 6 will migrate this
    to a UUID once the branch is rebased onto main.
    """
    with app.app_context():
        fake_film_id = 999999

        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(user_id=sample_user, film_id=fake_film_id)
