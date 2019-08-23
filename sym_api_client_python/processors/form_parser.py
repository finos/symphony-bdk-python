

class FormParser:
    """
    FormParser class takes elements_action_data as its only parameter.
    elements action data is a json object passed from DataFeedEventService
    to the ElementsListenerImplementation class.  The elements_action_data json
    follows the structure below:

    {
        "actionStream": {
            "streamId": "0YeiA-neZa1PrdHy1L82jX___pQjntU-dA"
        },
        "formStream": {
            "streamId": "YuK1c2y2yuie6+UfQnjSPX///pQEn69idA=="
        },
        "formMessageId": "q79Am2NpPefaV42JogMPRX///pQEDbD+dA==5653",
        "formId": "form_id",
        "formValues": {
            "action": "submit_button",
            "name_01": "John Doe",
            "country": "opt1",
            "example_radio": "option_01",
            "checkbox_1": "value01",
            "checkbox_2": "value02",
            "comment": "In my opinion..."
            }
        }

    This class provides methods to the developer to easily access data in this
    elements action payload corresponding to each element in the form.
    """

    def __init__(self):
        pass

    def get_stream_id(self, elements_action_data):
        if 'stream' in elements_action_data['payload']['symphonyElementsAction'] and 'id' in elements_action_data['payload']['symphonyElementsAction']['stream']:
            return elements_action_data['payload']['symphonyElementsAction']['stream']['id']
        if 'formStream' in elements_action_data['payload']['symphonyElementsAction'] and 'streamId' in elements_action_data['payload']['symphonyElementsAction']['formStream']:
            return elements_action_data['payload']['symphonyElementsAction']['formStream']['streamId'].rstrip('=').replace('/', '_').replace('+', '-')

    def get_action_stream_id(self, elements_action_data):
        """
        returns streamId for the actionStream.
        actionStream is where the formMessage is sent, this is a hidden stream
        so that the encryption context is between user and bot only and not everyone else on the room
        """
        if elements_action_data['payload']['symphonyElementsAction']['actionStream'] != None and elements_action_data['payload']['symphonyElementsAction']['actionStream']['streamId'] != None:
            return elements_action_data['payload']['symphonyElementsAction']['actionStream']['streamId']

    def get_form_message_id(self, elements_action_data):
        """
        returns formMessageId corresponding to the element sent:
        """
        return elements_action_data['payload']['symphonyElementsAction']['formMessageId']

    def get_form_Id(self, elements_action_data):
        """
        returns the unique formId assosiated with this form element
        """
        return elements_action_data['payload']['symphonyElementsAction']['formId']

    def get_form_values(self, elements_action_data):
        """
        returns a dictionary of key value pairs in the following format:
        {
            "element_name": "element_value"
        }

        For Example:

        {
            "action": "submit_button",
            "name_01": "John Doe",
            "country": "opt1",
            "example_radio": "option_01",
            "checkbox_1": "value01",
            "checkbox_2": "value02",
            "comment": "In my opinion..."

        }
        """

        return elements_action_data['payload']['symphonyElementsAction']['formValues']

    def get_action(self, elements_action_data):
        """
        returns name of button that submitted the form when clicked
        """
        return elements_action_data['payload']['symphonyElementsAction']['formValues']['action']

    def get_initiator_userId(self, elements_action_data):
        """
        returns id of user that submitted the form
        """
        return elements_action_data['initiator']['user']['userId']
