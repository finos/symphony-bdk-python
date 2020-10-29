import json
from .format_json import convert_to_dict
from .expense_approval_class import ExpenseApprovalForm

reeds_expense_form = ExpenseApprovalForm('food report', 'summary of lunch expenses', 'Reed Feldman')
reeds_expense_form.upload_expenses([('conde', 'august 22', 12.00), ('fooda', 'august 21', 10.00), ('bento', 'august 2', 12.00)])

def generate_expense_approval_table(expense_approval_table_data):
    return dict(message = """<messageML>
                                <form id="expense-approval-form">
                                    <div class="entity" data-entity-id="ExpenseApprovalForm">
                                    <span>
                                        <h3>${entity['ExpenseApprovalForm'].person_name}</h3>
                                    </span>
                                        <table>
                                            <thead>
                                                <tr>
                                                    <td>Expense Name:</td>
                                                    <td>Expense Date:</td>
                                                    <td>Expense Amount:</td>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <#foreach expense in entity['ExpenseApprovalForm'].expenses>
                                                    <tr>
                                                        <td>${expense.expense_name}</td>
                                                        <td>${expense.expense_date}</td>
                                                        <td>$${expense.expense_price}</td>
                                                    </tr>
                                                </#foreach>
                                            </tbody>
                                            <tfoot>
                                                <tr>
                                                    <td> </td>
                                                    <td> </td>
                                                    <td>Total: $${entity['ExpenseApprovalForm'].report_total}</td>
                                                </tr>
                                            </tfoot>
                                        </table>
                                        <button type="action" name="approve-button">Approve</button>
                                        <button type="action" name="reject-button">Reject</button>
                                        <button type="action" name="add-expense">Add</button>
                                        <button type="action" name="remove-expense">Remove</button>


                                    </div>
                                </form>
                            </messageML>

        """,

            data = json.dumps(expense_approval_table_data, default=convert_to_dict, indent=4, sort_keys=True)

        )

def generate_add_expense_form(expense_approval_table_data):
    return dict(message = """<messageML>
                                <form id="add-expense-form">
                                    <div class="entity" data-entity-id="ExpenseApprovalForm">
                                        <span>
                                            <h3>Add Expense for: ${entity['ExpenseApprovalForm'].person_name}</h3>
                                        </span>
                                        <span>
                                            <text-field name="add-vendor-textfield" placeholder="Enter a vender: " required="true"/>
                                            <br/>
                                            <text-field name="add-date-textfield" placeholder="Enter a Date: " required="true"/>
                                            <br/>
                                            <text-field name="add-price-textfield" placeholder="Enter a Price: " required="true"/>
                                            <br/>
                                            <button type="action" name="add-expense-button">Submit</button>
                                        </span>
                                    </div>
                                </form>
                            </messageML>

        """,

            data = json.dumps(expense_approval_table_data, default=convert_to_dict, indent=4, sort_keys=True)

        )
def generate_remove_expense_form(expense_approval_table_data):
    return dict(message = """<messageML>
                                <form id="remove-approval-form">
                                    <div class="entity" data-entity-id="ExpenseApprovalForm">
                                    <span>
                                        <h3>${entity['ExpenseApprovalForm'].person_name}</h3>
                                    </span>
                                        <table>
                                            <thead>
                                                <tr>
                                                    <td>Expense Name:</td>
                                                    <td>Expense Date:</td>
                                                    <td>Expense Amount:</td>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <#foreach expense in entity['ExpenseApprovalForm'].expenses>
                                                    <tr>
                                                        <td>${expense.expense_name}</td>
                                                        <td>${expense.expense_date}</td>
                                                        <td>$${expense.expense_price}</td>
                                                        <td>
                                                            <button type="action" name="remove-expense-button ${expense?index}">Remove</button>
                                                        </td>
                                                    </tr>
                                                </#foreach>
                                            </tbody>
                                            <tfoot>
                                                <tr>
                                                    <td> </td>
                                                    <td> </td>
                                                    <td>Total: $${entity['ExpenseApprovalForm'].report_total}</td>
                                                </tr>
                                            </tfoot>
                                        </table>
                                    </div>
                                </form>
                            </messageML>

        """,

            data = json.dumps(expense_approval_table_data, default=convert_to_dict, indent=4, sort_keys=True)

        )
