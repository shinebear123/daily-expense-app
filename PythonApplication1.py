import calendar
import json
import os
import tkinter as tk
from datetime import date
from tkinter import messagebox, ttk


DATA_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "daily_expense_data.json"
)


class CalendarPopup(tk.Toplevel):
    def __init__(self, parent, selected_date, on_select):
        super().__init__(parent)

        self.title("날짜 선택")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.on_select = on_select
        self.selected_date = selected_date
        self.display_year = selected_date.year
        self.display_month = selected_date.month

        self.create_widgets()
        self.update_calendar()

    def create_widgets(self):
        header = ttk.Frame(self)
        header.pack(fill="x", padx=12, pady=12)

        ttk.Button(
            header,
            text="◀",
            width=4,
            command=self.previous_month
        ).pack(side="left")

        self.month_label = ttk.Label(
            header,
            font=("맑은 고딕", 12, "bold"),
            anchor="center"
        )
        self.month_label.pack(side="left", expand=True)

        ttk.Button(
            header,
            text="▶",
            width=4,
            command=self.next_month
        ).pack(side="right")

        self.calendar_frame = ttk.Frame(self)
        self.calendar_frame.pack(padx=12, pady=(0, 12))

        ttk.Button(
            self,
            text="오늘",
            command=self.select_today
        ).pack(pady=(0, 12))

    def update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.config(
            text=f"{self.display_year}년 {self.display_month}월"
        )

        weekdays = ("월", "화", "수", "목", "금", "토", "일")

        for column, weekday in enumerate(weekdays):
            label = ttk.Label(
                self.calendar_frame,
                text=weekday,
                width=5,
                anchor="center"
            )
            label.grid(row=0, column=column, padx=2, pady=4)

        month_calendar = calendar.monthcalendar(
            self.display_year,
            self.display_month
        )

        for row, week in enumerate(month_calendar, start=1):
            for column, day_number in enumerate(week):
                if day_number == 0:
                    continue

                button = ttk.Button(
                    self.calendar_frame,
                    text=str(day_number),
                    width=5,
                    command=lambda day=day_number: self.select_day(day)
                )
                button.grid(row=row, column=column, padx=2, pady=2)

    def previous_month(self):
        if self.display_month == 1:
            self.display_year -= 1
            self.display_month = 12
        else:
            self.display_month -= 1

        self.update_calendar()

    def next_month(self):
        if self.display_month == 12:
            self.display_year += 1
            self.display_month = 1
        else:
            self.display_month += 1

        self.update_calendar()

    def select_day(self, day_number):
        selected = date(
            self.display_year,
            self.display_month,
            day_number
        )
        self.on_select(selected)
        self.destroy()

    def select_today(self):
        self.on_select(date.today())
        self.destroy()


class DailyExpenseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("하루용돈 소비 기록")
        self.root.geometry("850x650")
        self.root.minsize(760, 560)

        self.data = self.load_data()

        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.allowance_var = tk.StringVar()
        self.category_var = tk.StringVar(value="식비")
        self.amount_var = tk.StringVar()
        self.memo_var = tk.StringVar()

        self.total_var = tk.StringVar(value="0원")
        self.remaining_var = tk.StringVar(value="0원")
        self.count_var = tk.StringVar(value="0건")

        self.create_widgets()
        self.load_selected_date()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            return {}

    def save_data(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    self.data,
                    file,
                    ensure_ascii=False,
                    indent=2
                )
        except OSError as error:
            messagebox.showerror(
                "저장 오류",
                f"데이터를 저장할 수 없습니다.\n{error}"
            )

    def create_widgets(self):
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(4, weight=1)

        title_label = ttk.Label(
            self.root,
            text="하루용돈 소비 기록",
            font=("맑은 고딕", 20, "bold")
        )
        title_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=(20, 10),
            sticky="w"
        )

        date_frame = ttk.LabelFrame(
            self.root,
            text="날짜 및 용돈 설정"
        )
        date_frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=5,
            sticky="ew"
        )
        date_frame.columnconfigure(5, weight=1)

        ttk.Label(
            date_frame,
            text="날짜"
        ).grid(
            row=0,
            column=0,
            padx=(12, 5),
            pady=12
        )

        date_entry = ttk.Entry(
            date_frame,
            textvariable=self.date_var,
            width=14
        )
        date_entry.grid(
            row=0,
            column=1,
            padx=5,
            pady=12
        )
        date_entry.bind(
            "<Return>",
            lambda event: self.load_selected_date()
        )

        ttk.Button(
            date_frame,
            text="달력 열기",
            command=self.open_calendar
                                                                                                                                                                                                                                                                    ).grid(
            row=0,
            column=2,
            padx=5,
            pady=12
        )

        ttk.Button(
            date_frame,
            text="날짜 불러오기",
            command=self.load_selected_date
        ).grid(
            row=0,
            column=3,
            padx=5,
            pady=12
        )

        ttk.Label(
            date_frame,
            text="오늘 용돈"
        ).grid(
            row=0,
            column=4,
            padx=(20, 5),
            pady=12
        )

        allowance_entry = ttk.Entry(
            date_frame,
            textvariable=self.allowance_var,
            width=14
        )
        allowance_entry.grid(
            row=0,
            column=5,
            padx=5,
            pady=12,
            sticky="w"
        )
        allowance_entry.bind(
            "<Return>",
            lambda event: self.save_allowance()
        )

        ttk.Button(
            date_frame,
            text="용돈 저장",
            command=self.save_allowance
        ).grid(
            row=0,
            column=6,
            padx=12,
            pady=12
        )

        input_frame = ttk.LabelFrame(
            self.root,
            text="소비 내역 입력"
        )
        input_frame.grid(
            row=2,
            column=0,
            padx=20,
            pady=10,
            sticky="ew"
        )
        input_frame.columnconfigure(5, weight=1)

        ttk.Label(
            input_frame,
            text="분류"
        ).grid(
            row=0,
            column=0,
            padx=(12, 5),
            pady=12
        )

        category_combo = ttk.Combobox(
            input_frame,
            textvariable=self.category_var,
            values=(
                "식비",
                "교통비",
                "간식",
                "쇼핑",
                "문화생활",
                "교육",
                "기타"
            ),
            state="readonly",
            width=12
        )
        category_combo.grid(
            row=0,
            column=1,
            padx=5,
            pady=12
        )

        ttk.Label(
            input_frame,
            text="금액"
        ).grid(
            row=0,
            column=2,
            padx=(20, 5),
            pady=12
        )

        amount_entry = ttk.Entry(
            input_frame,
            textvariable=self.amount_var,
            width=14
        )
        amount_entry.grid(
            row=0,
            column=3,
            padx=5,
            pady=12
        )
        amount_entry.bind(
            "<Return>",
            lambda event: self.add_expense()
        )

        ttk.Label(
            input_frame,
            text="내용"
        ).grid(
            row=0,
            column=4,
            padx=(20, 5),
            pady=12
        )

        memo_entry = ttk.Entry(
            input_frame,
            textvariable=self.memo_var
        )
        memo_entry.grid(
            row=0,
            column=5,
            padx=5,
            pady=12,
            sticky="ew"
        )
        memo_entry.bind(
            "<Return>",
            lambda event: self.add_expense()
        )

        ttk.Button(
            input_frame,
            text="소비 추가",
            command=self.add_expense
        ).grid(
            row=0,
            column=6,
            padx=12,
            pady=12
        )

        summary_frame = ttk.Frame(self.root)
        summary_frame.grid(
            row=3,
            column=0,
            padx=20,
            pady=(0, 10),
            sticky="ew"
        )

        for column in range(3):
            summary_frame.columnconfigure(column, weight=1)

        self.create_summary_box(
            summary_frame,
            0,
            "총 소비 금액",
            self.total_var
        )
        self.create_summary_box(
            summary_frame,
            1,
            "남은 용돈",
            self.remaining_var
        )
        self.create_summary_box(
            summary_frame,
            2,
            "소비 건수",
            self.count_var
        )

        list_frame = ttk.LabelFrame(
            self.root,
            text="소비 내역"
        )
        list_frame.grid(
            row=4,
            column=0,
            padx=20,
            pady=5,
            sticky="nsew"
        )
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("category", "amount", "memo")

        self.expense_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="extended"
        )

        self.expense_tree.heading("category", text="분류")
        self.expense_tree.heading("amount", text="금액")
        self.expense_tree.heading("memo", text="내용")

        self.expense_tree.column(
            "category",
            width=130,
            anchor="center"
        )
        self.expense_tree.column(
            "amount",
            width=150,
            anchor="e"
        )
        self.expense_tree.column(
            "memo",
            width=450,
            anchor="w"
        )

        scrollbar = ttk.Scrollbar(
            list_frame,
            orient="vertical",
            command=self.expense_tree.yview
        )
        self.expense_tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.expense_tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        button_frame = ttk.Frame(self.root)
        button_frame.grid(
            row=5,
            column=0,
            padx=20,
            pady=(10, 20),
            sticky="e"
        )

        ttk.Button(
            button_frame,
            text="선택 항목 삭제",
            command=self.delete_selected_expenses
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="오늘 날짜로 이동",
            command=self.go_to_today
        ).pack(side="left", padx=5)

        ttk.Button(
            button_frame,
            text="종료",
            command=self.root.destroy
        ).pack(side="left", padx=5)

    def create_summary_box(self, parent, column, title, variable):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(
            row=0,
            column=column,
            padx=5,
            sticky="ew"
        )

        label = ttk.Label(
            frame,
            textvariable=variable,
            font=("맑은 고딕", 14, "bold"),
            anchor="center"
        )
        label.pack(
            fill="x",
            padx=10,
            pady=12
        )

    def get_selected_date(self):
        selected_date = self.date_var.get().strip()

        try:
            date.fromisoformat(selected_date)
        except ValueError:
            messagebox.showwarning(
                "날짜 형식 오류",
                "날짜는 YYYY-MM-DD 형식으로 입력하세요.\n"
                "예: 2026-11-20"
            )
            return None

        return selected_date

    def get_current_day_data(self):
        selected_date = self.get_selected_date()

        if selected_date is None:
            return None, None

        if selected_date not in self.data:
            self.data[selected_date] = {
                "allowance": 0,
                "expenses": []
            }

        return selected_date, self.data[selected_date]

    def open_calendar(self):
        try:
            selected_date = date.fromisoformat(
                self.date_var.get().strip()
            )
        except ValueError:
            selected_date = date.today()

        CalendarPopup(
            self.root,
            selected_date,
            self.set_selected_date
        )

    def set_selected_date(self, selected_date):
        self.date_var.set(selected_date.isoformat())
        self.load_selected_date()

    def save_allowance(self):
        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        allowance_text = (
            self.allowance_var.get()
            .replace(",", "")
            .strip()
        )

        if not allowance_text:
            allowance_text = "0"

        try:
            allowance = int(allowance_text)

            if allowance < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "입력 오류",
                "용돈은 0 이상의 정수로 입력하세요."
            )
            return

        day_data["allowance"] = allowance
        self.save_data()
        self.update_summary()

        messagebox.showinfo(
            "저장 완료",
            f"{selected_date}의 용돈이 저장되었습니다."
        )

    def add_expense(self):
        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        amount_text = (
            self.amount_var.get()
            .replace(",", "")
            .strip()
        )
        memo = self.memo_var.get().strip()

        if not amount_text:
            messagebox.showwarning(
                "입력 오류",
                "소비 금액을 입력하세요."
            )
            return

        try:
            amount = int(amount_text)

            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "입력 오류",
                "소비 금액은 1 이상의 정수로 입력하세요."
            )
            return

        if not memo:
            messagebox.showwarning(
                "입력 오류",
                "소비 내용을 입력하세요."
            )
            return

        day_data["expenses"].append(
            {
                "category": self.category_var.get(),
                "amount": amount,
                "memo": memo
            }
        )

        self.save_data()

        self.amount_var.set("")
        self.memo_var.set("")

        self.update_expense_list()

        self.update_summary()

    def delete_selected_expenses(self):
        selected_items = self.expense_tree.selection()

        if not selected_items:
            messagebox.showwarning(
                "선택 필요",
                "삭제할 소비 내역을 선택하세요."
            )
            return

        if not messagebox.askyesno(
            "삭제 확인",
            "선택한 소비 내역을 삭제하시겠습니까?"
        ):
            return

        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        indexes = sorted(
            [int(item_id) for item_id in selected_items],
            reverse=True
        )

        for index in indexes:
            if 0 <= index < len(day_data["expenses"]):
                day_data["expenses"].pop(index)

        self.save_data()
        self.update_expense_list()
        self.update_summary()

    def load_selected_date(self):
        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        self.allowance_var.set(
            str(day_data.get("allowance", 0))
        )
        self.update_expense_list()
        self.update_summary()

    def go_to_today(self):
        self.date_var.set(date.today().isoformat())
        self.load_selected_date()

    def update_expense_list(self):
        for item_id in self.expense_tree.get_children():
            self.expense_tree.delete(item_id)

        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        for index, expense in enumerate(
            day_data.get("expenses", [])
        ):
            self.expense_tree.insert(
                "",
                "end",
                iid=str(index),
                values=(
                    expense.get("category", "기타"),
                    f"{expense.get('amount', 0):,}원",
                    expense.get("memo", "")
                )
            )

    def update_summary(self):
        selected_date, day_data = self.get_current_day_data()

        if selected_date is None:
            return

        expenses = day_data.get("expenses", [])
        allowance = int(day_data.get("allowance", 0))

        total = sum(
            int(expense.get("amount", 0))
            for expense in expenses
        )
        remaining = allowance - total

        self.total_var.set(f"{total:,}원")
        self.remaining_var.set(f"{remaining:,}원")
        self.count_var.set(f"{len(expenses)}건")


def main():
    root = tk.Tk()
    DailyExpenseApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
