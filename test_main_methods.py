import pytest
import tkinter as tk
from unittest.mock import patch, MagicMock, call
import datetime
from main import CurrencyConverterApp


class TestMainMethods:
    """Test class for main.py methods without GUI initialization"""
    
    def test_is_loan_invalid_positive_value(self):
        """Test is_loan_invalid with positive value"""
        with patch('main.messagebox') as mock_messagebox:
            # Create a minimal app instance for testing
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.log_text = MagicMock()
            
            result = app.is_loan_invalid(100.0, "Test message")
            
            assert result is False
            mock_messagebox.showerror.assert_not_called()
            app.log_text.configure.assert_not_called()
    
    def test_is_loan_invalid_zero_value(self):
        """Test is_loan_invalid with zero value"""
        with patch('main.messagebox') as mock_messagebox:
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.log_text = MagicMock()
            
            test_message = "Test error message"
            result = app.is_loan_invalid(0.0, test_message)
            
            assert result is True
            mock_messagebox.showerror.assert_called_once_with("Ошибка", test_message)
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_is_loan_invalid_negative_value(self):
        """Test is_loan_invalid with negative value"""
        with patch('main.messagebox') as mock_messagebox:
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.log_text = MagicMock()
            
            test_message = "Test negative error"
            result = app.is_loan_invalid(-50.0, test_message)
            
            assert result is True
            mock_messagebox.showerror.assert_called_once_with("Ошибка", test_message)
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_calculate_loan_success(self):
        """Test successful loan calculation"""
        with patch('main.messagebox') as mock_messagebox:
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            
            # Mock UI components
            app.loan_var = MagicMock()
            app.loan_var.get.return_value = 100000.0
            app.loan_time_var = MagicMock()
            app.loan_time_var.get.return_value = 12
            app.annual_interest_var = MagicMock()
            app.annual_interest_var.get.return_value = 17.0
            app.monthly_label = MagicMock()
            app.loan_sum_label = MagicMock()
            app.interest_label = MagicMock()
            app.convert_btn = MagicMock()
            app.log_text = MagicMock()
            
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
    
    def test_calculate_loan_invalid_loan_amount(self):
        """Test calculate_loan with invalid loan amount"""
        with patch('main.messagebox') as mock_messagebox:
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            
            app.loan_var = MagicMock()
            app.loan_var.get.return_value = 0.0  # Invalid amount
            app.loan_time_var = MagicMock()
            app.loan_time_var.get.return_value = 12
            app.annual_interest_var = MagicMock()
            app.annual_interest_var.get.return_value = 17.0
            app.monthly_label = MagicMock()
            app.loan_sum_label = MagicMock()
            app.interest_label = MagicMock()
            app.convert_btn = MagicMock()
            app.log_text = MagicMock()
            
            with patch.object(app, 'is_loan_invalid') as mock_invalid:
                mock_invalid.return_value = True  # First call returns True (invalid)
                
                app.calculate_loan()
                
                # Should return early, no calculations should happen
                app.monthly_label.config.assert_not_called()
                app.loan_sum_label.config.assert_not_called()
                app.interest_label.config.assert_not_called()
                app.convert_btn.config.assert_not_called()
    
    def test_convert_success(self):
        """Test successful currency conversion"""
        with patch('main.messagebox') as mock_messagebox, \
             patch('main.get_saved_rate') as mock_get_rate:
            
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.base_var = MagicMock()
            app.base_var.get.return_value = "RUB"
            app.target_var = MagicMock()
            app.target_var.get.return_value = "USD"
            app.payment = 1000.0  # Set payment amount
            app.result_label = MagicMock()
            app.log_text = MagicMock()
            
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
    
    def test_convert_none_rate(self):
        """Test convert when rate is None"""
        with patch('main.messagebox') as mock_messagebox, \
             patch('main.get_saved_rate') as mock_get_rate:
            
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.base_var = MagicMock()
            app.base_var.get.return_value = "RUB"
            app.target_var = MagicMock()
            app.target_var.get.return_value = "USD"
            app.payment = 1000.0
            app.result_label = MagicMock()
            app.log_text = MagicMock()
            
            mock_get_rate.return_value = None
            
            app.convert()
            
            # Should return early without updating UI
            app.result_label.config.assert_not_called()
            app.log_text.configure.assert_not_called()
            mock_messagebox.showerror.assert_not_called()
    
    def test_convert_exception(self):
        """Test convert with exception handling"""
        with patch('main.messagebox') as mock_messagebox, \
             patch('main.get_saved_rate') as mock_get_rate:
            
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.base_var = MagicMock()
            app.base_var.get.return_value = "RUB"
            app.target_var = MagicMock()
            app.target_var.get.return_value = "USD"
            app.payment = 1000.0
            app.result_label = MagicMock()
            app.log_text = MagicMock()
            
            mock_get_rate.side_effect = Exception("Database error")
            
            app.convert()
            
            mock_messagebox.showerror.assert_called_once_with("Ошибка", "Database error")
            app.log_text.configure.assert_called()
            app.log_text.insert.assert_called()
    
    def test_update_db_success(self):
        """Test successful database update"""
        with patch('main.messagebox') as mock_messagebox, \
             patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.target_var = MagicMock()
            app.target_var.get.return_value = "USD"
            app.log_text = MagicMock()
            
            mock_rates = {
                "USD": {"Value": 75.0},
                "EUR": {"Value": 82.0},
                "GBP": {"Value": 95.0}
            }
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
    
    def test_update_db_empty_rates(self):
        """Test update_db with empty rates"""
        with patch('main.messagebox') as mock_messagebox, \
             patch('main.fetch_rates') as mock_fetch, \
             patch('main.save_rate') as mock_save:
            
            app = CurrencyConverterApp.__new__(CurrencyConverterApp)
            app.target_var = MagicMock()
            app.target_var.get.return_value = "USD"
            app.log_text = MagicMock()
            
            mock_fetch.return_value = {}
            
            app.update_db()
            
            mock_save.assert_not_called()
            mock_messagebox.showinfo.assert_called_once_with(
                "Успех", "Сохранено 0 курсов в базе данных."
            )
    
    def test_log_method(self):
        """Test the log method functionality"""
        app = CurrencyConverterApp.__new__(CurrencyConverterApp)
        app.log_text = MagicMock()
        
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

if __name__ == "__main__":
    pytest.main([__file__])
