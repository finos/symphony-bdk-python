import logging

from symphony.bdk.core.activity.api import AbstractActivity, ActivityContext
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction

logger = logging.getLogger(__name__)


class FormReplyContext(ActivityContext[V4SymphonyElementsAction]):
    """
    Default implementation of the :py:class`ActivityContext` handled by the :py:class:`FormReplyActivity`
    """

    def __init__(self, initiator: V4Initiator, source_event: V4SymphonyElementsAction):
        self._form_id = source_event.form_id
        self._form_values = source_event.form_values
        super().__init__(initiator, source_event)

    @property
    def form_id(self) -> str:
        return self._form_id

    @property
    def form_values(self) -> dict:
        return self._form_values

    def get_form_value(self, field_name: str) -> str:
        """Get the value of specified form field

        :param field_name: the form field name
        :return: the form field value if it is present, None otherwise
        """
        return self.form_values.get(field_name)


class FormReplyActivity(AbstractActivity[FormReplyContext]):
    """
    A form reply activity corresponds to an Elements form submission.
    """

    def matches(self, context: FormReplyContext) -> bool:
        pass

    def on_activity(self, context: FormReplyContext):
        pass
