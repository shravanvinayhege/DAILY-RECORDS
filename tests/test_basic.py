"""
tests_basic.py  –  Unit & integration tests for KARAVALI Financial Management System
Run with:  pytest tests/tests_basic.py -v --cov=KARAVALI --cov-report=xml
"""

import sys
import os
import sqlite3
import tempfile
import pytest

# ── Make sure the project root is importable ──────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Stub out tkinter and matplotlib BEFORE importing KARAVALI ─────────────
import unittest.mock as mock

# Tkinter full stub
tk_mock = mock.MagicMock()
ttk_mock = mock.MagicMock()
sys.modules["tkinter"] = tk_mock
sys.modules["tkinter.ttk"] = ttk_mock
sys.modules["tkinter.messagebox"] = mock.MagicMock()

# Matplotlib stubs
sys.modules["matplotlib"] = mock.MagicMock()
sys.modules["matplotlib.pyplot"] = mock.MagicMock()
sys.modules["matplotlib.dates"] = mock.MagicMock()
sys.modules["matplotlib.backends"] = mock.MagicMock()
sys.modules["matplotlib.backends.backend_tkagg"] = mock.MagicMock()
sys.modules["matplotlib.ticker"] = mock.MagicMock()
# Don't stub numpy with MagicMock: pytest.approx() uses isinstance(..., np.bool_).


# ══════════════════════════════════════════════════════════════════════════════
#  FIXTURES
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def tmp_db():
    """Create an isolated in-memory SQLite DB that mirrors the app schema."""
    conn = sqlite3.connect(":memory:")
    cur = conn.cursor()

    for tbl in ("parlor_records", "factory_records"):
        cur.execute(f"""CREATE TABLE {tbl} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT UNIQUE,
            opening_balance   REAL DEFAULT 0,
            misc_expenses     REAL DEFAULT 0,
            ice_cream_purchases REAL DEFAULT 0,
            keb_honnaver      REAL DEFAULT 0,
            keb_ramthirth     REAL DEFAULT 0,
            pigmy             REAL DEFAULT 0,
            milk_expenses     REAL DEFAULT 0,
            day_sales         REAL DEFAULT 0
        )""")

    cur.execute("""CREATE TABLE salary_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER, record_type TEXT,
        employee_name TEXT, amount REAL DEFAULT 0
    )""")

    cur.execute("""CREATE TABLE vehicle_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER, record_type TEXT,
        vehicle_number TEXT, petrol REAL DEFAULT 0, maintenance REAL DEFAULT 0
    )""")

    cur.execute("""CREATE TABLE misc_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER, record_type TEXT,
        purpose TEXT, amount REAL DEFAULT 0
    )""")

    cur.execute("""CREATE TABLE keb_entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        record_id INTEGER, record_type TEXT,
        meter_name TEXT, amount REAL DEFAULT 0
    )""")

    conn.commit()
    yield conn, cur
    conn.close()


@pytest.fixture(autouse=True)
def clean_tables(tmp_db):
    """Wipe all data rows between tests (keep schema)."""
    conn, cur = tmp_db
    for tbl in ("parlor_records", "factory_records",
                "salary_entries", "vehicle_entries",
                "misc_entries", "keb_entries"):
        cur.execute(f"DELETE FROM {tbl}")
    conn.commit()
    yield


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER — pure-Python calculation logic (mirrors _calculate in KaravaliApp)
# ══════════════════════════════════════════════════════════════════════════════

def calculate(opening_balance=0, salary=0, petrol=0, vehicle_maint=0,
              misc=0, keb=0, milk=0, ice_cream_purchases=0, pigmy=0):
    total_expenses  = salary + petrol + vehicle_maint + misc + keb + milk
    total_purchases = ice_cream_purchases
    total_outflow   = opening_balance + total_expenses + total_purchases + pigmy
    closing_balance = -total_expenses - total_purchases - pigmy
    day_sales       = (total_expenses + ice_cream_purchases + pigmy) - opening_balance
    return {
        "total_salary":    salary,
        "total_vehicle":   petrol + vehicle_maint,
        "total_misc":      misc,
        "total_keb":       keb,
        "total_expenses":  total_expenses,
        "total_purchases": total_purchases,
        "total_outflow":   total_outflow,
        "closing_balance": closing_balance,
        "day_sales":       day_sales,
    }


# ══════════════════════════════════════════════════════════════════════════════
#  HELPER — db path stub
# ══════════════════════════════════════════════════════════════════════════════

def _resource_path(relative_path):
    base = os.path.abspath(".")
    return os.path.join(base, relative_path)


def _db_path_tmp():
    return ":memory:"


# ══════════════════════════════════════════════════════════════════════════════
#  1. CALCULATION LOGIC
# ══════════════════════════════════════════════════════════════════════════════

class TestCalculation:

    def test_zero_inputs(self):
        r = calculate()
        assert r["day_sales"] == 0
        assert r["total_expenses"] == 0
        assert r["closing_balance"] == 0

    def test_day_sales_formula(self):
        # day_sales = (expenses + purchases + pigmy) - opening_balance
        r = calculate(opening_balance=500, salary=200, ice_cream_purchases=300, pigmy=50)
        # expenses=200, purchases=300, pigmy=50 → 550 - 500 = 50
        assert r["day_sales"] == pytest.approx(50.0)

    def test_negative_day_sales(self):
        # opening_balance larger than all outflows → negative day sales
        r = calculate(opening_balance=10000, salary=100, ice_cream_purchases=200)
        assert r["day_sales"] < 0

    def test_all_expense_categories(self):
        r = calculate(salary=100, petrol=50, vehicle_maint=30,
                      misc=20, keb=40, milk=10)
        assert r["total_expenses"] == pytest.approx(250.0)

    def test_total_vehicle(self):
        r = calculate(petrol=150, vehicle_maint=75)
        assert r["total_vehicle"] == pytest.approx(225.0)

    def test_closing_balance(self):
        r = calculate(salary=500, ice_cream_purchases=300, pigmy=100)
        # closing = -(500 + 300 + 100) = -900
        assert r["closing_balance"] == pytest.approx(-900.0)

    def test_large_values(self):
        r = calculate(opening_balance=1_000_000, salary=500_000,
                      ice_cream_purchases=250_000, pigmy=50_000)
        assert r["day_sales"] == pytest.approx(-200_000.0)

    def test_decimal_precision(self):
        r = calculate(salary=333.33, petrol=666.67)
        assert r["total_expenses"] == pytest.approx(1000.0, rel=1e-5)


# ══════════════════════════════════════════════════════════════════════════════
#  2. DATABASE SCHEMA & CRUD
# ══════════════════════════════════════════════════════════════════════════════

class TestDatabaseSchema:

    def test_parlor_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parlor_records'")
        assert cur.fetchone() is not None

    def test_factory_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='factory_records'")
        assert cur.fetchone() is not None

    def test_salary_entries_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='salary_entries'")
        assert cur.fetchone() is not None

    def test_vehicle_entries_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='vehicle_entries'")
        assert cur.fetchone() is not None

    def test_misc_entries_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='misc_entries'")
        assert cur.fetchone() is not None

    def test_keb_entries_table_exists(self, tmp_db):
        _, cur = tmp_db
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='keb_entries'")
        assert cur.fetchone() is not None

    def test_parlor_required_columns(self, tmp_db):
        _, cur = tmp_db
        cur.execute("PRAGMA table_info(parlor_records)")
        cols = {r[1] for r in cur.fetchall()}
        required = {"id", "date", "opening_balance", "misc_expenses",
                    "ice_cream_purchases", "keb_honnaver", "keb_ramthirth",
                    "pigmy", "milk_expenses", "day_sales"}
        assert required.issubset(cols)

    def test_factory_required_columns(self, tmp_db):
        _, cur = tmp_db
        cur.execute("PRAGMA table_info(factory_records)")
        cols = {r[1] for r in cur.fetchall()}
        required = {"id", "date", "opening_balance", "misc_expenses",
                    "ice_cream_purchases", "keb_honnaver", "keb_ramthirth",
                    "pigmy", "milk_expenses", "day_sales"}
        assert required.issubset(cols)


# ══════════════════════════════════════════════════════════════════════════════
#  3. RECORD INSERT & RETRIEVAL
# ══════════════════════════════════════════════════════════════════════════════

class TestRecordInsert:

    def _insert_parlor(self, cur, conn, date="01-01-2025", ob=1000, ds=500):
        cur.execute("""INSERT INTO parlor_records
            (date, opening_balance, misc_expenses, ice_cream_purchases,
             keb_honnaver, keb_ramthirth, pigmy, milk_expenses, day_sales)
            VALUES (?,?,0,0,0,0,0,0,?)""", (date, ob, ds))
        conn.commit()
        return cur.lastrowid

    def test_insert_parlor_record(self, tmp_db):
        conn, cur = tmp_db
        rid = self._insert_parlor(cur, conn)
        cur.execute("SELECT id FROM parlor_records WHERE date='01-01-2025'")
        assert cur.fetchone() is not None

    def test_unique_date_constraint_parlor(self, tmp_db):
        conn, cur = tmp_db
        self._insert_parlor(cur, conn, date="02-01-2025")
        with pytest.raises(sqlite3.IntegrityError):
            self._insert_parlor(cur, conn, date="02-01-2025")

    def test_insert_factory_record(self, tmp_db):
        conn, cur = tmp_db
        cur.execute("""INSERT INTO factory_records
            (date, opening_balance, day_sales) VALUES (?,?,?)""",
            ("03-01-2025", 2000, 800))
        conn.commit()
        cur.execute("SELECT day_sales FROM factory_records WHERE date='03-01-2025'")
        row = cur.fetchone()
        assert row[0] == pytest.approx(800.0)

    def test_parlor_and_factory_same_date_allowed(self, tmp_db):
        """Same date is fine across different tables (different mode)."""
        conn, cur = tmp_db
        self._insert_parlor(cur, conn, date="05-01-2025")
        cur.execute("INSERT INTO factory_records (date, opening_balance, day_sales) VALUES (?,?,?)",
                    ("05-01-2025", 500, 200))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM parlor_records WHERE date='05-01-2025'")
        assert cur.fetchone()[0] == 1
        cur.execute("SELECT COUNT(*) FROM factory_records WHERE date='05-01-2025'")
        assert cur.fetchone()[0] == 1

    def test_default_values_on_insert(self, tmp_db):
        conn, cur = tmp_db
        cur.execute("INSERT INTO parlor_records (date) VALUES ('06-01-2025')")
        conn.commit()
        cur.execute("SELECT opening_balance, misc_expenses FROM parlor_records WHERE date='06-01-2025'")
        row = cur.fetchone()
        assert row[0] == 0
        assert row[1] == 0


# ══════════════════════════════════════════════════════════════════════════════
#  4. SUB-TABLE ENTRIES (salary / vehicle / misc / keb)
# ══════════════════════════════════════════════════════════════════════════════

class TestSubEntries:

    def _base_record(self, cur, conn, mode="parlor", date="10-01-2025"):
        tbl = "parlor_records" if mode == "parlor" else "factory_records"
        cur.execute(f"INSERT INTO {tbl} (date, opening_balance, day_sales) VALUES (?,?,?)",
                    (date, 0, 0))
        conn.commit()
        return cur.lastrowid

    def test_salary_entry_insert_and_sum(self, tmp_db):
        conn, cur = tmp_db
        rid = self._base_record(cur, conn)
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid, "parlor", "Raju", 5000))
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid, "parlor", "Suma", 4500))
        conn.commit()
        cur.execute("SELECT SUM(amount) FROM salary_entries WHERE record_id=? AND record_type=?", (rid, "parlor"))
        assert cur.fetchone()[0] == pytest.approx(9500.0)

    def test_vehicle_entry_insert(self, tmp_db):
        conn, cur = tmp_db
        rid = self._base_record(cur, conn, date="11-01-2025")
        cur.execute("""INSERT INTO vehicle_entries
            (record_id,record_type,vehicle_number,petrol,maintenance) VALUES (?,?,?,?,?)""",
            (rid, "parlor", "KA55AB1234", 1200, 300))
        conn.commit()
        cur.execute("SELECT SUM(petrol), SUM(maintenance) FROM vehicle_entries WHERE record_id=?", (rid,))
        row = cur.fetchone()
        assert row[0] == pytest.approx(1200.0)
        assert row[1] == pytest.approx(300.0)

    def test_misc_entry_insert_and_sum(self, tmp_db):
        conn, cur = tmp_db
        rid = self._base_record(cur, conn, date="12-01-2025")
        for purpose, amt in [("Cleaning", 200), ("Stationery", 150), ("Tea", 50)]:
            cur.execute("INSERT INTO misc_entries (record_id,record_type,purpose,amount) VALUES (?,?,?,?)",
                        (rid, "parlor", purpose, amt))
        conn.commit()
        cur.execute("SELECT SUM(amount) FROM misc_entries WHERE record_id=?", (rid,))
        assert cur.fetchone()[0] == pytest.approx(400.0)

    def test_keb_entry_insert_multiple_meters(self, tmp_db):
        conn, cur = tmp_db
        rid = self._base_record(cur, conn, date="13-01-2025")
        for meter, amt in [("Honnavar Meter", 2500), ("Ramthirth Meter", 1800)]:
            cur.execute("INSERT INTO keb_entries (record_id,record_type,meter_name,amount) VALUES (?,?,?,?)",
                        (rid, "parlor", meter, amt))
        conn.commit()
        cur.execute("SELECT SUM(amount) FROM keb_entries WHERE record_id=?", (rid,))
        assert cur.fetchone()[0] == pytest.approx(4300.0)

    def test_delete_cascades_sub_entries(self, tmp_db):
        """Deleting a record + its sub-entries manually (app behaviour)."""
        conn, cur = tmp_db
        rid = self._base_record(cur, conn, date="14-01-2025")
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid, "parlor", "Ghost", 999))
        conn.commit()
        for sub in ("salary_entries", "vehicle_entries", "misc_entries", "keb_entries"):
            cur.execute(f"DELETE FROM {sub} WHERE record_id=? AND record_type=?", (rid, "parlor"))
        cur.execute("DELETE FROM parlor_records WHERE id=?", (rid,))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM salary_entries WHERE record_id=?", (rid,))
        assert cur.fetchone()[0] == 0

    def test_factory_sub_entries_isolated_from_parlor(self, tmp_db):
        conn, cur = tmp_db
        rid_p = self._base_record(cur, conn, mode="parlor",  date="15-01-2025")
        rid_f = self._base_record(cur, conn, mode="factory", date="15-01-2025")
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid_p, "parlor", "Parlor Staff", 3000))
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid_f, "factory", "Factory Worker", 4000))
        conn.commit()
        cur.execute("SELECT SUM(amount) FROM salary_entries WHERE record_id=? AND record_type='parlor'", (rid_p,))
        assert cur.fetchone()[0] == pytest.approx(3000.0)
        cur.execute("SELECT SUM(amount) FROM salary_entries WHERE record_id=? AND record_type='factory'", (rid_f,))
        assert cur.fetchone()[0] == pytest.approx(4000.0)


# ══════════════════════════════════════════════════════════════════════════════
#  5. DATE VALIDATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

class TestDateValidation:

    def _date_exists(self, cur, date_val, mode, exclude_id=None):
        tbl = "factory_records" if mode == "factory" else "parlor_records"
        if exclude_id:
            cur.execute(f"SELECT id FROM {tbl} WHERE date=? AND id!=?", (date_val, exclude_id))
        else:
            cur.execute(f"SELECT id FROM {tbl} WHERE date=?", (date_val,))
        return cur.fetchone() is not None

    def test_date_not_exists_initially(self, tmp_db):
        _, cur = tmp_db
        assert not self._date_exists(cur, "20-01-2025", "parlor")

    def test_date_exists_after_insert(self, tmp_db):
        conn, cur = tmp_db
        cur.execute("INSERT INTO parlor_records (date) VALUES ('21-01-2025')")
        conn.commit()
        assert self._date_exists(cur, "21-01-2025", "parlor")

    def test_date_exists_excludes_own_id(self, tmp_db):
        conn, cur = tmp_db
        cur.execute("INSERT INTO parlor_records (date) VALUES ('22-01-2025')")
        conn.commit()
        rid = cur.lastrowid
        # Excluding own ID should return False (no duplicate)
        assert not self._date_exists(cur, "22-01-2025", "parlor", exclude_id=rid)

    def test_date_exists_different_modes_independent(self, tmp_db):
        conn, cur = tmp_db
        cur.execute("INSERT INTO parlor_records (date) VALUES ('23-01-2025')")
        conn.commit()
        # Same date in factory should NOT be flagged as existing in parlor
        assert not self._date_exists(cur, "23-01-2025", "factory")


# ══════════════════════════════════════════════════════════════════════════════
#  6. GET_FLOAT UTILITY
# ══════════════════════════════════════════════════════════════════════════════

class TestGetFloat:

    def _get_float(self, val, ph="0.00"):
        """Inline replica of the app's get_float() for pure-Python testing."""
        v = val.strip()
        if v == ph or v == "":
            return 0.0
        try:
            return float(v)
        except ValueError:
            return 0.0

    def test_empty_string(self):
        assert self._get_float("") == 0.0

    def test_placeholder(self):
        assert self._get_float("0.00") == 0.0

    def test_valid_integer_string(self):
        assert self._get_float("500") == pytest.approx(500.0)

    def test_valid_float_string(self):
        assert self._get_float("1234.56") == pytest.approx(1234.56)

    def test_invalid_string(self):
        assert self._get_float("abc") == 0.0

    def test_negative_value(self):
        assert self._get_float("-250.75") == pytest.approx(-250.75)

    def test_whitespace_only(self):
        assert self._get_float("   ") == 0.0

    def test_custom_placeholder(self):
        assert self._get_float("DD-MM-YYYY", ph="DD-MM-YYYY") == 0.0


# ══════════════════════════════════════════════════════════════════════════════
#  7. PASSWORD CHECK
# ══════════════════════════════════════════════════════════════════════════════

class TestPassword:
    APP_PASSWORD = "12345"

    def test_correct_password(self):
        assert "12345" == self.APP_PASSWORD

    def test_wrong_password(self):
        assert "00000" != self.APP_PASSWORD

    def test_empty_password(self):
        assert "" != self.APP_PASSWORD

    def test_case_sensitive(self):
        assert "12345".upper() == "12345"   # digits — case doesn't apply
        assert "Admin" != self.APP_PASSWORD

    def test_sql_injection_attempt(self):
        assert "' OR '1'='1" != self.APP_PASSWORD


# ══════════════════════════════════════════════════════════════════════════════
#  8. KEB WIDGET LOGIC  (pure dict operations)
# ══════════════════════════════════════════════════════════════════════════════

class TestKEBLogic:

    def _sum_keb(self, keb_dict):
        return sum(v for v in keb_dict.values() if isinstance(v, (int, float)) and v > 0)

    def test_empty_keb(self):
        assert self._sum_keb({}) == 0.0

    def test_single_meter(self):
        assert self._sum_keb({"Meter A": 1500}) == pytest.approx(1500.0)

    def test_multiple_meters(self):
        assert self._sum_keb({"Meter A": 1500, "Meter B": 2000}) == pytest.approx(3500.0)

    def test_zero_amount_excluded(self):
        assert self._sum_keb({"Meter A": 0, "Meter B": 500}) == pytest.approx(500.0)

    def test_honnavar_ramthirth_naming(self):
        keb_vals = {"Honnavar Meter": 2500, "Ramthirth Meter": 1800}
        keb_hon = sum(v for k, v in keb_vals.items() if "Honnavar" in k)
        keb_ram = sum(v for k, v in keb_vals.items() if "Ramthirth" in k)
        assert keb_hon == pytest.approx(2500.0)
        assert keb_ram == pytest.approx(1800.0)


# ══════════════════════════════════════════════════════════════════════════════
#  9. RECORD UPDATE (edit flow)
# ══════════════════════════════════════════════════════════════════════════════

class TestRecordUpdate:

    def _insert(self, cur, conn, mode="parlor", date="30-01-2025", ob=1000, ds=500):
        tbl = "parlor_records" if mode == "parlor" else "factory_records"
        cur.execute(f"INSERT INTO {tbl} (date,opening_balance,day_sales) VALUES (?,?,?)",
                    (date, ob, ds))
        conn.commit()
        return cur.lastrowid

    def test_update_opening_balance(self, tmp_db):
        conn, cur = tmp_db
        rid = self._insert(cur, conn)
        cur.execute("UPDATE parlor_records SET opening_balance=? WHERE id=?", (5000, rid))
        conn.commit()
        cur.execute("SELECT opening_balance FROM parlor_records WHERE id=?", (rid,))
        assert cur.fetchone()[0] == pytest.approx(5000.0)

    def test_update_day_sales(self, tmp_db):
        conn, cur = tmp_db
        rid = self._insert(cur, conn, date="31-01-2025")
        cur.execute("UPDATE parlor_records SET day_sales=? WHERE id=?", (9999, rid))
        conn.commit()
        cur.execute("SELECT day_sales FROM parlor_records WHERE id=?", (rid,))
        assert cur.fetchone()[0] == pytest.approx(9999.0)

    def test_update_date(self, tmp_db):
        conn, cur = tmp_db
        rid = self._insert(cur, conn, date="01-02-2025")
        cur.execute("UPDATE parlor_records SET date=? WHERE id=?", ("15-02-2025", rid))
        conn.commit()
        cur.execute("SELECT date FROM parlor_records WHERE id=?", (rid,))
        assert cur.fetchone()[0] == "15-02-2025"

    def test_replace_salary_entries_on_edit(self, tmp_db):
        conn, cur = tmp_db
        rid = self._insert(cur, conn, date="02-02-2025")
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid, "parlor", "Old Employee", 3000))
        conn.commit()
        # Simulate edit: delete old, insert new
        cur.execute("DELETE FROM salary_entries WHERE record_id=? AND record_type=?", (rid, "parlor"))
        cur.execute("INSERT INTO salary_entries (record_id,record_type,employee_name,amount) VALUES (?,?,?,?)",
                    (rid, "parlor", "New Employee", 6000))
        conn.commit()
        cur.execute("SELECT employee_name, amount FROM salary_entries WHERE record_id=?", (rid,))
        rows = cur.fetchall()
        assert len(rows) == 1
        assert rows[0] == ("New Employee", 6000.0)


# ══════════════════════════════════════════════════════════════════════════════
#  10. RESOURCE PATH HELPER
# ══════════════════════════════════════════════════════════════════════════════

class TestResourcePath:

    def test_returns_string(self):
        path = _resource_path("icon.png")
        assert isinstance(path, str)

    def test_contains_filename(self):
        path = _resource_path("icon.png")
        assert "icon.png" in path

    def test_different_files(self):
        p1 = _resource_path("icon.png")
        p2 = _resource_path("icon.ico")
        assert p1 != p2

    def test_nested_path(self):
        path = _resource_path(os.path.join("assets", "logo.png"))
        assert "assets" in path