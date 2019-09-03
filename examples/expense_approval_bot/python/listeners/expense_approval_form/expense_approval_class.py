import jinja2
from jinja2 import Template

expense_data = {
    "ExpenseApprovalForm": {
        "expenses": [
            {
                "expense_date": "august 22",
                "expense_name": "conde",
                "expense_price": 12.00
            },
            {
                "expense_date": "august 21",
                "expense_name": "fooda",
                "expense_price": 10.00
            },
            {
                "expense_date": "august 2",
                "expense_name": "bento",
                "expense_price": 12.00
            }
        ],
        "person_name": "Reed Feldman",
        "report_name": "food report",
        "report_summary": "summary of lunch expenses",
        "report_total": 34.00
    }
}

def upload_expense(expense):
    for name, date, price, in expense:
        expense_data['ExpenseApprovalForm']['report_total'] += price
        expense_data['ExpenseApprovalForm']['expenses'].append(dict(expense_name = name,
                                                                 expense_date = date,
                                                                 expense_price = price))
def remove_item(expense_index):
    print(expense_index)
    item_price = float(expense_data['ExpenseApprovalForm']['expenses'][expense_index]['expense_price'])

    expense_data['ExpenseApprovalForm']['report_total'] -= item_price
    del expense_data['ExpenseApprovalForm']['expenses'][expense_index]

def render_expense_approval_form(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read(), trim_blocks=True, lstrip_blocks=True)
    html = template.render(expense_data)
    return dict(message = html)

def render_add_expense_form(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read(), trim_blocks=True, lstrip_blocks=True)
    html = template.render(expense_data)
    return dict(message = html)

def render_remove_expense_form(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read(), trim_blocks=True, lstrip_blocks=True)
    html = template.render(expense_data)
    return dict(message = html)

# upload_expense([('conde', 'august 22', 12.00), ('fooda', 'august 21', 10.00), ('bento', 'august 2', 12.00)])
# print(render_expense_approval_form('./html/expense_approval_table.html'))
