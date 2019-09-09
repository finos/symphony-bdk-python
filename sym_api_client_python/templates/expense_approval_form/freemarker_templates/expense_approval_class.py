import json

class ExpenseApprovalForm:

    def __init__(self, report_name, report_summary, person_name):

        self.ExpenseApprovalForm = dict(
            report_name = report_name,
            report_summary = report_summary,
            person_name = person_name,
            expenses = [],
            report_total = 0
        )


    def upload_expenses(self, expenses):
        for name, date, price, in expenses:
            self.ExpenseApprovalForm['report_total'] += price
            self.ExpenseApprovalForm['expenses'].append(dict(expense_name = name,
                                                             expense_date = date,
                                                             expense_price = price))

    def remove_item(self, expense_index):
        item_price = float(self.ExpenseApprovalForm['expenses'][expense_index]['expense_price'])
        self.ExpenseApprovalForm['report_total'] -= item_price
        del self.ExpenseApprovalForm['expenses'][expense_index]
