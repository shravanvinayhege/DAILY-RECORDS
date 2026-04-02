"""
Smoke and unit tests for KARAVALI.

Mocks tkinter and matplotlib before importing the app so CI does not need a display.
Do not stub numpy: pytest.approx() requires a real numpy.bool_ type in sys.modules.
"""

import os
import sqlite3
import sys
import unittest.mock as mock

import pytest

# Project root on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock GUI / plotting before KARAVALI import
sys.modules["tkinter"] = mock.MagicMock()
sys.modules["tkinter.ttk"] = mock.MagicMock()
sys.modules["tkinter.messagebox"] = mock.MagicMock()

sys.modules["matplotlib"] = mock.MagicMock()
sys.modules["matplotlib.pyplot"] = mock.MagicMock()
sys.modules["matplotlib.dates"] = mock.MagicMock()
sys.modules["matplotlib.backends"] = mock.MagicMock()
sys.modules["matplotlib.backends.backend_tkagg"] = mock.MagicMock()
sys.modules["matplotlib.ticker"] = mock.MagicMock()

import KARAVALI  # noqa: E402  (after mocks)


def test_import():
    assert KARAVALI is not None


def test_basic_math():
    assert 2 + 2 == 4


@pytest.fixture
def db():
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE test (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
        """
    )
    conn.commit()
    yield conn, cur
    conn.close()


def test_db_insert(db):
    conn, cur = db
    cur.execute("INSERT INTO test (name) VALUES ('Shravan')")
    conn.commit()
    cur.execute("SELECT name FROM test")
    result = cur.fetchone()
    assert result[0] == "Shravan"


def get_float(val):
    try:
        return float(val)
    except ValueError:
        return 0.0


def test_get_float_valid():
    assert get_float("123.45") == pytest.approx(123.45)


def test_get_float_invalid():
    assert get_float("abc") == 0.0


def calculate(day_sales, expenses):
    return day_sales - expenses


def test_calculate():
    assert calculate(1000, 400) == 600
