import jinja2
from jinja2 import Template

form_template = {
  "form_id": 'example-form-id'
};

def render_form(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(form_template)
    return html

# print(render_form('forms/form.html'))

button_template = {
    "name": "example-button",
    "type": "action",
    "text": "Submit"
}

def render_button(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(button_template)
    return html

# print(render_button('forms/button.html'))

text_field_template = {
    "name":"exmaple-text-field",
    "placeholder": "example-placeholder",
    "required": "true",
    "masked": "true",
    "minlength": 1,
    "maxlength": 128
}

def render_text_field(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(text_field_template)
    return html

# print(render_text_field('forms/text_field.html'))

text_area_template = {
    "name":"exmaple-text-area",
    "placeholder": "example-placeholder",
    "required": "true",
}

def render_text_area(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(text_area_template)
    return html

# print(render_text_area('forms/text_area.html'))

checkbox_template = {
"name":"example-name",
"value":"example-value",
"checked": "false",
"text":"Red"
}

def render_checkbox(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(checkbox_template)
    return html

# print(render_checkbox('forms/checkbox.html'))

radio_button_template = {
"name":"example-name",
"value":"example-value",
"checked": "false",
"text":"Red"
}

def render_radio_button(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(radio_button_template)
    return html

# print(render_radio_button('forms/radio_button.html'))

dropdown_menu_template = {
"name":"dropdown-name",
"required": "true",
"options": [{"value":"value1", "selected":"true", "text":"First Option"},
            {"value":"value2", "selected":"false", "text":"Second Option"},
            {"value":"value3", "selected":"true", "text":"Third Option"} ]

}

def render_dropdown_menu(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(dropdown_menu_template)
    return html

# print(render_dropdown_menu('forms/dropdown_menu.html'))

person_selector_template = {
"name":"person-selector-name",
"placeholder":"example-placeholder",
"required":"true"
}

def render_person_selector(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read())
    html = template.render(person_selector_template)
    return html

# print(render_dropdown_menu('forms/person_selector.html'))

table_select_template = {
"select":{
    "position":"left",
    "type":"button"
    },
"header_list": ["H1", "H2", "H3"],
"body": [["A1", "B1", "C1"],
         ["A2", "B2", "C2"],
         ["A3", "B3", "C3"]],
"footer_list": ["F1", "F2", "F3"]
}

def render_table_select(path_to_html_form):
    with open(path_to_html_form) as file:
        template = Template(file.read(), trim_blocks=True, lstrip_blocks=True)
    html = template.render(table_select_template)
    return html

print(render_table_select('forms/table_select.html'))
