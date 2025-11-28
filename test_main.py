import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock, call
import datetime
from main import CurrencyConverterApp


class TestCurrencyConverterApp:
    """Test class for CurrencyConverterApp methods"""
    
    @pytest.fixture
    def app(self):
        """Create a test instance of CurrencyConverterApp"""
        with patch('main.init_db'), \
             patch.object(tk.Tk, '__init__', return_value=None), \
             patch.object(tk.Tk, 'title'), \
             patch.object(tk.Tk, 'geometry'), \
             patch.object(tk.Tk, 'resizable'), \
             patch.object(tk.Tk, 'mainloop'), \
             patch('main.ttk.Label'), \
             patch('main.ttk.Entry'), \
             patch('main.ttk.Button'), \
             patch('main.ttk.Combobox'), \
             patch('main.tk.DoubleVar'), \
             patch('main.tk.IntVar'), \
             patch('main.tk.StringVar'), \
             patch('main.tk.Text'):
            app = CurrencyConverterApp()
            # Mock the tkinter components to avoid GUI issues
            app.monthly_label = MagicMock()
            app.loan_sum_label = MagicMock()
            app.interest_label = MagicMock()
            app.convert_btn = MagicMock()
            app.result_label = MagicMock()
            app.log_text = MagicMock()
            return app
    
    @pytest.fixture
    def mock_messagebox(self):
        """Mock messagebox for testing"""
        with patch('main.messagebox') as mock_mb:
            yield mock_mb
    
    def test_log_method(self, app):
        """Test the log method functionality"""
        test_message = "Test log message"
        
        with patch('main.datetime') as mock_datetime:
            mock_now = MagicMock()
            mock_now.strftime.return_value = "14:30:25"
            mock_datetime.datetime.now.return_value = mock_now
            
            app.log(test_message)
            
            # Verify log_text methods were called
            app.log_text.configure.assert_has_calls([
                call(state="normal"),
                call(state="disabled")
            ])
            app.log_text.insert.assert_called_once_with(tk.END, "14:30:25 - Test log message\n")
            app.log_text.see.assert_called_once_with(tk.END)
    
    def test_is_loan_invalid_positive_value(self, app, mock_messagebox):
        """Test is_loan_invalid with positive value"""
        result = app.is_loan_invalid(100.0, "Test message")
        
        assert result is False
        mock_messagebox.showerror.assert_not_called()
        app.log_text.configure.assert_not_called()
    
    def test_is_loan_invalid_zero_value(self, app, mock_messagebox):
        """Test is_loan_invalid with zero value"""
        test_message = "Test error message"
        result = app.is_loan_invalid(0.0, test_message)
        
        assert result is True
        mock_messagebox.showerror.assert_called_once_with("Ошибка", test_message)
        app.log_text.configure.assert_called()
        app.log_text.insert.assert_called()
    
    def test_is_loan_invalid_negative_value(self, app, mock_messagebox):
        """Test is_loan_invalid with negative value"""
        test_message = "Test negative error"
        result = app.is_loan_invalid(-50.0, test_message)
        
        assert result is True
        mock_messagebox.showerror.assert_called_once_with("Ошибка", test_message)
        app.log_text.configure.assert_called()
        app.log_text.insert.assert_called()
    
    def test_calculate_loan_success(self, app, mock_messagebox):
        """Test successful loan calculation"""
        # Set up valid values
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 100000.0
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 12
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 17.0
        
        with patch.object(app, 'is_loan_invalid', return_value=False):
            app.calculate_loan()
            
            # Verify calculations
            expected_monthly = 17.0 / 12 / 100  # 0.014166...
            expected_payment = (100000.0 * expected_monthly) / (1 - (1 + expected_monthly) ** -12)
            expected_monthly_total = round(expected_payment, 2)
            expected_loan_sum_total = round(expected_payment * 12, 2)
            expected_interest_total = round(expected_payment * 12 - 100000.0, 2)
            
            # Verify UI updates
            app.monthly_label.config.assert_called_once_with(
                text=f"Ежемесячный платеж: {expected_monthly_total} RUB"
            )
            app.loan_sum_label.config.assert_called_once_with(
                text=f"Сумма всех платежей: {expected_loan_sum_total} RUB"
            )
            app.interest_label.config.assert_called_once_with(
                text=f"Начисленные проценты: {expected_interest_total} RUB"
            )
            app.convert_btn.config.assert_called_once_with(state=tk.ACTIVE)
            
            # Verify logging
            assert app.log_text.configure.call_count >= 6  # At least 3 log calls * 2 configure calls each
    
    def test_calculate_loan_invalid_loan_amount(self, app, mock_messagebox):
        """Test calculate_loan with invalid loan amount"""
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 0.0  # Invalid amount
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 12
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 17.0
        
        with patch.object(app, 'is_loan_invalid') as mock_invalid:
            mock_invalid.return_value = True  # First call returns True (invalid)
            
            app.calculate_loan()
            
            # Should return early, no calculations should happen
            app.monthly_label.config.assert_not_called()
            app.loan_sum_label.config.assert_not_called()
            app.interest_label.config.assert_not_called()
            app.convert_btn.config.assert_not_called()
    
    def test_calculate_loan_invalid_loan_time(self, app, mock_messagebox):
        """Test calculate_loan with invalid loan time"""
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 100000.0
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 0  # Invalid time
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 17.0
        
        with patch.object(app, 'is_loan_invalid') as mock_invalid:
            mock_invalid.side_effect = [False, True, False]  # Second call returns True
            
            app.calculate_loan()
            
            # Should return early after second validation
            app.monthly_label.config.assert_not_called()
            app.loan_sum_label.config.assert_not_called()
            app.interest_label.config.assert_not_called()
            app.convert_btn.config.assert_not_called()
    
    def test_calculate_loan_invalid_interest_rate(self, app, mock_messagebox):
        """Test calculate_loan with invalid interest rate"""
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 100000.0
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 12
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 0.0  # Invalid rate
        
        with patch.object(app, 'is_loan_invalid') as mock_invalid:
            mock_invalid.side_effect = [False, False, True]  # Third call returns True
            
            app.calculate_loan()
            
            # Should return early after third validation
            app.monthly_label.config.assert_not_called()
            app.loan_sum_label.config.assert_not_called()
            app.interest_label.config.assert_not_called()
            app.convert_btn.config.assert_not_called()
    
    def test_calculate_loan_edge_cases(self, app, mock_messagebox):
        """Test calculate_loan with edge case values"""
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 1.0  # Minimum valid amount
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 1  # Minimum valid time
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 0.01  # Minimum valid rate
        
        with patch.object(app, 'is_loan_invalid', return_value=False):
            app.calculate_loan()
            
            # Should complete successfully
            app.monthly_label.config.assert_called_once()
            app.loan_sum_label.config.assert_called_once()
            app.interest_label.config.assert_called_once()
            app.convert_btn.config.assert_called_once_with(state=tk.ACTIVE)
    
    def test_convert_success(self, app, mock_messagebox):
        """Test successful currency conversion"""
        app.base_var = MagicMock()
        app.base_var.get.return_value = "RUB"
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        app.payment = 1000.0  # Set payment amount
        
        with patch('main.get_saved_rate') as mock_get_rate:
            mock_get_rate.return_value = 75.0  # 1 USD = 75 RUB
            
            app.convert()
            
            # Verify conversion calculation
            expected_converted = round(1000.0 / 75.0, 2)  # 13.33
            
            app.result_label.config.assert_called_once_with(
                text=f"1000.00 RUB = {expected_converted:.2f} USD"
            )
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
            mock_messagebox.showerror.assert_not_called()
    
    def test_convert_none_rate(self, app, mock_messagebox):
        """Test convert when rate is None"""
        app.base_var = MagicMock()
        app.base_var.get.return_value = "RUB"
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        app.payment = 1000.0
        
        with patch('main.get_saved_rate') as mock_get_rate:
            mock_get_rate.return_value = None
            
            app.convert()
            
            # Should return early without updating UI
            app.result_label.config.assert_not_called()
            app.log_text.configure.assert_not_called()
            mock_messagebox.showerror.assert_not_called()
    
    def test_convert_exception(self, app, mock_messagebox):
        """Test convert with exception handling"""
        app.base_var = MagicMock()
        app.base_var.get.return_value = "RUB"
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        app.payment = 1000.0
        
        with patch('main.get_saved_rate') as mock_get_rate:
            mock_get_rate.side_effect = Exception("Database error")
            
            app.convert()
            
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "Database error")
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_convert_currency_case_handling(self, app, mock_messagebox):
        """Test convert with different currency cases"""
        app.base_var = MagicMock()
        app.base_var.get.return_value = "rub"  # lowercase
        app.target_var = MagicMock()
        app.target_var.get.return_value = "usd"  # lowercase
        app.payment = 1000.0
        
        with patch('main.get_saved_rate') as mock_get_rate:
            mock_get_rate.return_value = 75.0
            
            app.convert()
            
            # Should convert to uppercase
            mock_get_rate.assert_called_once_with("USD")
            app.result_label.config.assert_called_once()
    
    def test_update_db_success(self, app, mock_messagebox):
        """Test successful database update"""
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        
        mock_rates = {
            "USD": {"Value": 75.0},
            "EUR": {"Value": 82.0},
            "GBP": {"Value": 95.0}
        }
        
        with patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            mock_fetch.return_value = mock_rates
            
            app.update_db()
            
            # Verify fetch_rates was called
            mock_fetch.assert_called_once()
            
            # Verify save_rate was called for each currency
            expected_calls = [
                call(1, "USD", 75.0),
                call(2, "EUR", 82.0),
                call(3, "GBP", 95.0)
            ]
            mock_save.assert_has_calls(expected_calls)
            
            # Verify success message
            mock_messagebox.showinfo.assert_called_once_with(
                "Успех", "Сохранено 3 курсов в базе данных."
            )
            
            # Verify logging
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_update_db_fetch_error(self, app, mock_messagebox):
        """Test update_db with fetch_rates error"""
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        
        with patch('main.fetch_rates') as mock_fetch:
            mock_fetch.side_effect = Exception("API error")
            
            app.update_db()
            
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "API error")
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_update_db_save_error(self, app, mock_messagebox):
        """Test update_db with save_rate error"""
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        
        mock_rates = {
            "USD": {"Value": 75.0}
        }
        
        with patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            mock_fetch.return_value = mock_rates
            mock_save.side_effect = Exception("Database error")
            
            app.update_db()
            
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "Database error")
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_update_db_empty_rates(self, app, mock_messagebox):
        """Test update_db with empty rates"""
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        
        with patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            mock_fetch.return_value = {}
            
            app.update_db()
            
            mock_save.assert_not_called()
            mock_messagebox.showinfo.assert_called_once_with(
                "Успех", "Сохранено 0 курсов в базе данных."
            )
    
    def test_update_db_large_dataset(self, app, mock_messagebox):
        """Test update_db with large dataset"""
        app.target_var = MagicMock()
        app.target_var.get.return_value = "USD"
        
        # Create large dataset
        large_rates = {}
        for i in range(100):
            currency = f"CUR{i:03d}"
            large_rates[currency] = {"Value": 1.0 + i * 0.1}
        
        with patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            mock_fetch.return_value = large_rates
            
            app.update_db()
            
            # Verify all rates were saved
            assert mock_save.call_count == 100
            
            # Verify success message
            mock_messagebox.showinfo.assert_called_once_with(
                "Успех", "Сохранено 100 курсов в базе данных."
            )
    
    def test_calculate_loan_mathematical_accuracy(self, app, mock_messagebox):
        """Test mathematical accuracy of loan calculations"""
        app.loan_var = MagicMock()
        app.loan_var.get.return_value = 100000.0
        app.loan_time_var = MagicMock()
        app.loan_time_var.get.return_value = 12
        app.annual_interest_var = MagicMock()
        app.annual_interest_var.get.return_value = 12.0  # 12% annual
        
        with patch.object(app, 'is_loan_invalid', return_value=False):
            app.calculate_loan()
            
            # Manual calculation verification
            monthly_rate = 12.0 / 12 / 100  # 0.01
            expected_payment = (100000.0 * monthly_rate) / (1 - (1 + monthly_rate) ** -12)
            expected_payment = round(expected_payment, 2)
            
            # Verify the payment calculation is correct (with small tolerance for floating point)
            assert abs(app.payment - expected_payment) < 0.01
            
            # Verify total calculations
            expected_total = round(expected_payment * 12, 2)
            expected_interest = round(expected_total - 100000.0, 2)
            
            # Check that the calculations are reasonable
            assert expected_payment > 0
            assert expected_total > 100000.0  # Total should be more than principal
            assert expected_interest > 0  # Interest should be positive


class TestAppInitialization:
    """Test app initialization and widget creation"""
    
    def test_app_initialization(self):
        """Test that app initializes without errors"""
        with patch('main.init_db'), \
             patch.object(tk.Tk, '__init__', return_value=None) as mock_init, \
             patch.object(tk.Tk, 'title'), \
             patch.object(tk.Tk, 'geometry'), \
             patch.object(tk.Tk, 'resizable'), \
             patch.object(tk.Tk, 'mainloop'), \
             patch('main.ttk.Label'), \
             patch('main.ttk.Entry'), \
             patch('main.ttk.Button'), \
             patch('main.ttk.Combobox'), \
             patch('main.tk.DoubleVar'), \
             patch('main.tk.IntVar'), \
             patch('main.tk.StringVar'), \
             patch('main.tk.Text'):
            app = CurrencyConverterApp()
            
            # Verify parent __init__ was called
            mock_init.assert_called_once()
    
    def test_widget_creation(self):
        """Test that widgets are created properly"""
        with patch('main.init_db'), \
             patch.object(tk.Tk, '__init__', return_value=None), \
             patch.object(tk.Tk, 'title'), \
             patch.object(tk.Tk, 'geometry'), \
             patch.object(tk.Tk, 'resizable'), \
             patch.object(tk.Tk, 'mainloop'), \
             patch('main.ttk.Label'), \
             patch('main.ttk.Entry'), \
             patch('main.ttk.Button'), \
             patch('main.ttk.Combobox'), \
             patch('main.tk.DoubleVar'), \
             patch('main.tk.IntVar'), \
             patch('main.tk.StringVar'), \
             patch('main.tk.Text'):
            app = CurrencyConverterApp()
            
            # Verify essential attributes exist
            assert hasattr(app, 'loan_var')
            assert hasattr(app, 'loan_time_var')
            assert hasattr(app, 'annual_interest_var')
            assert hasattr(app, 'base_var')
            assert hasattr(app, 'target_var')
            assert hasattr(app, 'monthly_label')
            assert hasattr(app, 'loan_sum_label')
            assert hasattr(app, 'interest_label')
            assert hasattr(app, 'convert_btn')
            assert hasattr(app, 'result_label')
            assert hasattr(app, 'log_text')


if __name__ == "__main__":
    pytest.main([__file__])
