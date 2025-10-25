import pytest
import sqlite3
import datetime
import os
import tempfile
from unittest.mock import patch, MagicMock
from db import save_rate, init_db, get_saved_rate, DB_NAME


class TestDatabaseOperations:
    """Test class for database operations in db.py"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        # Create a temporary file for the database
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        # Store the original DB_NAME
        original_db_name = DB_NAME
        
        # Patch the DB_NAME to use our temporary database
        with patch('db.DB_NAME', temp_file.name):
            # Initialize the database
            init_db()
            yield temp_file.name
        
        # Cleanup: remove the temporary file
        try:
            os.unlink(temp_file.name)
        except (PermissionError, FileNotFoundError):
            # File might be locked or already deleted, ignore
            pass
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing"""
        return {
            'id': 1,
            'currency': 'USD',
            'rate': 1.0
        }
    
    def test_init_db_creates_table(self, temp_db):
        """Test that init_db creates the rates table with correct schema"""
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        
        # Check if table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rates'")
        table_exists = cur.fetchone() is not None
        assert table_exists, "Table 'rates' should be created"
        
        # Check table schema
        cur.execute("PRAGMA table_info(rates)")
        columns = cur.fetchall()
        
        expected_columns = [
            ('id', 'INTEGER', 0, None, 1),  # PRIMARY KEY
            ('currency', 'TEXT', 1, None, 0),  # NOT NULL
            ('rate', 'REAL', 1, None, 0),  # NOT NULL
            ('fetched_at', 'TEXT', 1, None, 0)  # NOT NULL
        ]
        
        assert len(columns) == 4, f"Expected 4 columns, got {len(columns)}"
        for i, (name, type_, not_null, default, pk) in enumerate(expected_columns):
            assert columns[i][1] == name, f"Column {i} name mismatch"
            assert columns[i][2] == type_, f"Column {i} type mismatch"
            assert columns[i][3] == not_null, f"Column {i} not_null mismatch"
            assert columns[i][5] == pk, f"Column {i} primary key mismatch"
        
        conn.close()
    
    def test_save_rate_new_record(self, temp_db, sample_data):
        """Test saving a new rate record"""
        save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT * FROM rates WHERE id = ?", (sample_data['id'],))
        result = cur.fetchone()
        
        assert result is not None, "Record should be saved"
        assert result[0] == sample_data['id']
        assert result[1] == sample_data['currency']
        assert result[2] == sample_data['rate']
        assert result[3] is not None, "fetched_at should not be None"
        
        conn.close()
    
    def test_save_rate_update_existing(self, temp_db, sample_data):
        """Test updating an existing rate record"""
        # Save initial record
        save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])
        
        # Update with new rate
        new_rate = 1.25
        save_rate(sample_data['id'], sample_data['currency'], new_rate)
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT rate FROM rates WHERE id = ?", (sample_data['id'],))
        result = cur.fetchone()
        
        assert result[0] == new_rate, "Rate should be updated"
        
        # Check that only one record exists (no duplicates)
        cur.execute("SELECT COUNT(*) FROM rates WHERE id = ?", (sample_data['id'],))
        count = cur.fetchone()[0]
        assert count == 1, "Should have exactly one record"
        
        conn.close()
    
    def test_save_rate_date_format(self, temp_db, sample_data):
        """Test that the date is formatted correctly"""
        with patch('db.datetime') as mock_datetime:
            # Mock datetime to return a specific date/time
            mock_now = MagicMock()
            mock_now.day = 15
            mock_now.month = 3
            mock_now.year = 2024
            mock_now.strftime.return_value = "14:30"
            mock_datetime.datetime.now.return_value = mock_now
            
            save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])
            
            conn = sqlite3.connect(temp_db)
            cur = conn.cursor()
            cur.execute("SELECT fetched_at FROM rates WHERE id = ?", (sample_data['id'],))
            result = cur.fetchone()
            
            expected_date = "15-3-2024 14:30"
            assert result[0] == expected_date, f"Expected {expected_date}, got {result[0]}"
            
            conn.close()
    
    def test_save_rate_multiple_currencies(self, temp_db):
        """Test saving rates for multiple currencies"""
        currencies = [
            (1, 'USD', 1.0),
            (2, 'EUR', 0.85),
            (3, 'GBP', 0.75),
            (4, 'JPY', 110.0)
        ]
        
        for id_val, currency, rate in currencies:
            save_rate(id_val, currency, rate)
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rates")
        count = cur.fetchone()[0]
        
        assert count == len(currencies), f"Expected {len(currencies)} records, got {count}"
        
        # Verify each record
        for id_val, currency, rate in currencies:
            cur.execute("SELECT currency, rate FROM rates WHERE id = ?", (id_val,))
            result = cur.fetchone()
            assert result[0] == currency
            assert result[1] == rate
        
        conn.close()
    
    def test_save_rate_edge_cases(self, temp_db):
        """Test edge cases for save_rate function"""
        # Test with zero rate
        save_rate(1, 'USD', 0.0)
        
        # Test with very large rate
        save_rate(2, 'JPY', 999999.99)
        
        # Test with negative rate (if that's valid for your use case)
        save_rate(3, 'TEST', -1.5)
        
        # Test with empty string currency
        save_rate(4, '', 1.0)
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rates")
        count = cur.fetchone()[0]
        
        assert count == 4, f"Expected 4 records, got {count}"
        
        conn.close()
    
    def test_save_rate_database_connection_error(self, sample_data):
        """Test handling of database connection errors"""
        with patch('db.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database connection failed")
            
            with pytest.raises(sqlite3.Error):
                save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])
    
    def test_save_rate_commit_error(self, temp_db, sample_data):
        """Test handling of commit errors"""
        with patch('db.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cur = MagicMock()
            mock_conn.cursor.return_value = mock_cur
            mock_conn.commit.side_effect = sqlite3.Error("Commit failed")
            mock_connect.return_value = mock_conn
            
            with pytest.raises(sqlite3.Error):
                save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])
    
    def test_save_rate_parameter_types(self, temp_db):
        """Test that save_rate handles different parameter types correctly"""
        # Test with string id (should work as SQLite is flexible)
        save_rate("1", "USD", 1.0)
        
        # Test with float rate
        save_rate(2, "EUR", 0.85)
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rates")
        count = cur.fetchone()[0]
        
        assert count == 2, f"Expected 2 records, got {count}"
        
        conn.close()
    
    def test_save_rate_sql_injection_protection(self, temp_db):
        """Test that save_rate is protected against SQL injection"""
        malicious_currency = "'; DROP TABLE rates; --"
        save_rate(1, malicious_currency, 1.0)
        
        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        
        # Check that table still exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='rates'")
        table_exists = cur.fetchone() is not None
        assert table_exists, "Table should still exist after attempted injection"
        
        # Check that the malicious string was stored as literal data
        cur.execute("SELECT currency FROM rates WHERE id = 1")
        result = cur.fetchone()
        assert result[0] == malicious_currency, "Malicious string should be stored as literal data"
        
        conn.close()


class TestGetSavedRate:
    """Test class specifically for get_saved_rate function"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()
        
        with patch('db.DB_NAME', temp_file.name):
            init_db()
            yield temp_file.name
        
        # Cleanup: remove the temporary file
        try:
            os.unlink(temp_file.name)
        except (PermissionError, FileNotFoundError):
            # File might be locked or already deleted, ignore
            pass
    
    def test_get_saved_rate_success(self, temp_db):
        """Test successful retrieval of a saved rate"""
        # Save a rate first
        save_rate(1, 'USD', 1.25)
        
        with patch('db.messagebox') as mock_messagebox:
            rate = get_saved_rate('USD')
            
            assert rate == 1.25, f"Expected rate 1.25, got {rate}"
            mock_messagebox.showerror.assert_not_called()
    
    def test_get_saved_rate_default_currency(self, temp_db):
        """Test get_saved_rate with default USD currency"""
        # Save a rate for USD
        save_rate(1, 'USD', 1.0)
        
        with patch('db.messagebox') as mock_messagebox:
            rate = get_saved_rate()  # No parameter, should default to USD
            
            assert rate == 1.0, f"Expected rate 1.0, got {rate}"
            mock_messagebox.showerror.assert_not_called()
    
    def test_get_saved_rate_nonexistent_currency(self, temp_db):
        """Test get_saved_rate with a currency that doesn't exist"""
        with patch('db.messagebox') as mock_messagebox:
            rate = get_saved_rate('NONEXISTENT')
            
            assert rate is None, "Rate should be None for nonexistent currency"
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "Обновите валютные курсы")
    
    def test_get_saved_rate_empty_database(self, temp_db):
        """Test get_saved_rate when database is empty"""
        with patch('db.messagebox') as mock_messagebox:
            rate = get_saved_rate('USD')
            
            assert rate is None, "Rate should be None when database is empty"
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "Обновите валютные курсы")
    
    def test_get_saved_rate_multiple_currencies(self, temp_db):
        """Test get_saved_rate with multiple currencies in database"""
        # Save multiple rates
        save_rate(1, 'USD', 1.0)
        save_rate(2, 'EUR', 0.85)
        save_rate(3, 'GBP', 0.75)
        
        with patch('db.messagebox') as mock_messagebox:
            # Test each currency
            usd_rate = get_saved_rate('USD')
            eur_rate = get_saved_rate('EUR')
            gbp_rate = get_saved_rate('GBP')
            
            assert usd_rate == 1.0, f"Expected USD rate 1.0, got {usd_rate}"
            assert eur_rate == 0.85, f"Expected EUR rate 0.85, got {eur_rate}"
            assert gbp_rate == 0.75, f"Expected GBP rate 0.75, got {gbp_rate}"
            mock_messagebox.showerror.assert_not_called()
    
    def test_get_saved_rate_case_sensitivity(self, temp_db):
        """Test get_saved_rate with different case sensitivity"""
        # Save rate with uppercase
        save_rate(1, 'USD', 1.0)
        
        with patch('db.messagebox') as mock_messagebox:
            # Test with lowercase
            rate_lower = get_saved_rate('usd')
            # Test with mixed case
            rate_mixed = get_saved_rate('Usd')
            
            # SQLite is case-insensitive by default, but let's test the behavior
            assert rate_lower is None, "Lowercase should not match uppercase"
            assert rate_mixed is None, "Mixed case should not match uppercase"
            assert mock_messagebox.showerror.call_count == 2
    
    def test_get_saved_rate_sql_injection_protection(self, temp_db):
        """Test that get_saved_rate is vulnerable to SQL injection (current implementation)"""
        # Save a normal rate
        save_rate(1, 'USD', 1.0)
        
        with patch('db.messagebox') as mock_messagebox:
            # Attempt SQL injection
            malicious_input = "'; DROP TABLE rates; --"
            rate = get_saved_rate(malicious_input)
            
            # The current implementation is vulnerable to SQL injection
            # This test documents the vulnerability
            assert rate is None, "Should return None for malicious input"
            mock_messagebox.showerror.assert_called_once()
    
    def test_get_saved_rate_database_connection_error(self):
        """Test get_saved_rate with database connection error"""
        with patch('db.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error("Database connection failed")
            
            # The current implementation doesn't handle connection errors,
            # so this test documents that the function will raise the exception
            with pytest.raises(sqlite3.Error, match="Database connection failed"):
                get_saved_rate('USD')

if __name__ == "__main__":
    pytest.main([__file__])
