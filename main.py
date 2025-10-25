import tkinter as tk
from tkinter import ttk, messagebox
import datetime

from db import init_db, save_rate, get_saved_rate
from api import fetch_rates

class CurrencyConverterApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Конвертер валют")
        self.geometry("465x670")
        self.resizable(False, False)

        self.create_widgets()
        init_db()

    def create_widgets(self):
        # Выбор cуммы кредита
        ttk.Label(self, text="Сумма кредита:").grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.loan_var = tk.DoubleVar(value=100000.0)
        ttk.Entry(self, textvariable=self.loan_var, width=12).grid(row=0, column=1, padx=10, pady=10, sticky="w")
        ttk.Label(self, text="RUB").grid(row=0, column=1, padx=100, pady=10, sticky="w")

        # Выбор срока кредита
        ttk.Label(self, text="Срок кредита:").grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.loan_time_var = tk.IntVar(value=12)
        ttk.Entry(self, textvariable=self.loan_time_var, width=12).grid(row=1, column=1, padx=10, pady=10, sticky="w")
        ttk.Label(self, text="Мес.").grid(row=1, column=1, padx=100, pady=10, sticky="w")

        # Выбор процентной ставки
        ttk.Label(self, text="Процентная ставка:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.annual_interest_var = tk.DoubleVar(value=17.0)
        ttk.Entry(self, textvariable=self.annual_interest_var, width=12).grid(row=2, column=1, padx=10, pady=10, sticky="w")
        ttk.Label(self, text="%").grid(row=2, column=1, padx=100, pady=10, sticky="w")

        # Кнопка расчета кредита
        ttk.Button(self, text="Рассчитать", command=self.calculate_loan).grid(row=3, column=0, columnspan=2, padx=10, pady=10)

        # Вывод результата кредита
        self.monthly_label = ttk.Label(self, text="Ежемесячный платеж: 0 RUB", font=("Arial", 12, "bold"))
        self.monthly_label.grid(row=4, column=0, columnspan=2, padx=10, pady=10)

        self.loan_sum_label = ttk.Label(self, text="Сумма всех платежей: 0 RUB", font=("Arial", 12, "bold"))
        self.loan_sum_label.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        self.interest_label = ttk.Label(self, text="Начисленные проценты: 0 RUB", font=("Arial", 12, "bold"))
        self.interest_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Начальная валюта
        ttk.Label(self, text="Базовая валюта:").grid(row=7, column=0, padx=10, pady=10, sticky="w")
        ttk.Label(self, text="RUB").grid(row=7, column=1, padx=10, pady=10, sticky="w")
        self.base_var = tk.StringVar(value="RUB")

        # Выбор искомой валюты
        ttk.Label(self, text="Целевая валюта:").grid(row=8, column=0, padx=10, pady=10, sticky="w")
        self.target_var = tk.StringVar(value="USD")
        self.target_entry = ttk.Combobox(self, textvariable=self.target_var, width=10,
                                         values=["USD", "EUR", "GBP", "JPY", "AUD"])
        self.target_entry.grid(row=8, column=1, padx=10, pady=10, sticky="w")

        # Кнопка конвертации
        self.convert_btn = ttk.Button(self, text="Конвертировать", command=self.convert)
        self.convert_btn.grid(row=9, column=0, columnspan=2, padx=10, pady=10)
        self.convert_btn.config(state=tk.DISABLED)

        # Вывод результата
        self.result_label = ttk.Label(self, text="", font=("Arial", 12, "bold"))
        self.result_label.grid(row=10, column=0, columnspan=2, padx=10, pady=10)

        # Кнопка обновления курса валют
        ttk.Button(self, text="Обновить курсы", command=self.update_db).grid(row=11, column=0, columnspan=2, padx=10, pady=10)

        # Логгер
        self.log_text = tk.Text(self, height=8, width=55, state="disabled", wrap="word")
        self.log_text.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

    def log(self, message: str):
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def is_loan_invalid(self, value: float, message: str) -> bool:
        if value <= 0.0:
            messagebox.showerror("Ошибка", message)
            self.log(message)
            return True
        
        return False

    def calculate_loan(self):
        if self.is_loan_invalid(self.loan_var.get(), "Сумма кредита должна быть > 0 RUB"): return
        if self.is_loan_invalid(self.loan_time_var.get(), "Срок кредита должен быть > 0 мес."): return
        if self.is_loan_invalid(self.annual_interest_var.get(), "Процентная ставка должна быть > 0 %"): return
        
        loan = self.loan_var.get()
        months = self.loan_time_var.get()
        annual = self.annual_interest_var.get()

        monthly = annual / 12 / 100
        self.payment = (loan * monthly) / (1 - (1 + monthly) ** -months)

        monthly_total = round(self.payment, 2)
        loan_sum_total = round(self.payment * months, 2)
        interest_total = round(self.payment * months - loan, 2)

        self.monthly_label.config(text=f"Ежемесячный платеж: {monthly_total} RUB")
        self.loan_sum_label.config(text=f"Сумма всех платежей: {loan_sum_total} RUB")
        self.interest_label.config(text=f"Начисленные проценты: {interest_total} RUB")

        self.log(f"Ежемесячный платеж: {monthly_total} RUB")
        self.log(f"Сумма всех платежей: {loan_sum_total} RUB")
        self.log(f"Начисленные проценты: {interest_total} RUB")

        self.convert_btn.config(state=tk.ACTIVE)

    def convert(self):
        base = self.base_var.get().upper()
        target = self.target_var.get().upper()
        amount = self.payment

        try:
            rate = get_saved_rate(target)
            if rate is None: return

            converted = amount / rate
            converted = round(converted, 2)
            self.result_label.config(text=f"{amount:.2f} {base} = {converted:.2f} {target}")
            self.log(f"Converted {amount} {base} → {converted:.2f} {target}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log(f"Conversion error: {e}")

    def update_db(self):
        target = self.target_var.get().upper()
        try:
            rates = fetch_rates()
            id = 1
            for target, rate in rates.items():
                save_rate(id, target, rate['Value'])
                id = id + 1
            self.log(f"Fetched {len(rates)} rates and saved to DB")
            messagebox.showinfo("Успех", f"Сохранено {len(rates)} курсов в базе данных.")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
            self.log(f"Fetch/save error: {e}")

if __name__ == "__main__":
    app = CurrencyConverterApp()
    app.mainloop()
