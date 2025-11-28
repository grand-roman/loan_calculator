import pytest
import sqlite3
import datetime
import os
import tempfile
from unittest.mock import patch, MagicMock
from db import save_rate, init_db, get_saved_rate, DB_NAME


class TestDatabseOperations:

    @pytest.fixture
    def temp_db(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
        temp_file.close()

        original_db_name = DB_NAME

        with patch('db.DB_NAME', temp_file.name):
            init_db()
            yield temp_file.name
        
        try:
            os.unlink(temp_file.name)
        except (PermissionError, FileNotFoundError):
            pass
    
    @pytest.fixture
    def sample_data(self):
        return {
            'id': 1,
            'currency': 'USD',
            'rate': 1.0
        }
    
    def test_save_rate_edge_cases(self, temp_db):
        save_rate(1, 'USD', 0.0)
        save_rate(2, 'JPY', 99999999.999)
        save_rate(3, 'TEST', -1.5)
        save_rate(4, '', 1.0)

        conn = sqlite3.connect(temp_db)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM rates")
        count = cur.fetchone()[0]

        assert count == 4, f'Expected 4 records, got {count}'

        conn.close()

    def test_save_rate_database_connection_error(self, sample_data):
        with patch('db.sqlite3.connect') as mock_connect:
            mock_connect.side_effect = sqlite3.Error('DB connection failed')

            with pytest.raises(sqlite3.Error):
                save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])

    def test_get_saved_rate_success(self, temp_db):
        save_rate(1, 'USD', 1.25)
        with patch('db.messagebox') as mock_messagebox:
            rate = get_saved_rate('USD')
            assert rate == 1.25, f'Expected rate 1.25, got {rate}'
            mock_messagebox.showerror.assert_not_called()

    def test_save_rate_commit_error(self, temp_db, sample_data):
        with patch('db.sqlite3.connect') as mock_connect:
            mock_conn = MagicMock()
            mock_cur = MagicMock()
            mock_conn.cursor.return_value = mock_cur
            mock_conn.commit.side_effect = sqlite3.Error('Commit Falied')
            mock_connect.return_value = mock_conn

            with pytest.raises(sqlite3.Error):
                save_rate(sample_data['id'], sample_data['currency'], sample_data['rate'])