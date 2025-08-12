import pytest

from symphony.bdk.core.activity.form import FormReplyActivity, FormReplyContext
from symphony.bdk.gen.agent_model.v4_initiator import V4Initiator
from symphony.bdk.gen.agent_model.v4_symphony_elements_action import V4SymphonyElementsAction


@pytest.fixture(name="activity")
def fixture_activity():
    class TestFormReplyActivity(FormReplyActivity):
        """Dummy test form reply activity"""

    return TestFormReplyActivity()


@pytest.fixture(name="context")
def fixture_context():
    return FormReplyContext(
        V4Initiator(),
        V4SymphonyElementsAction(
            form_id="test_form", form_message_id="message_id", form_values={"key": "value"}
        ),
    )


def test_matcher(activity, context):
    def dummy_matcher(passed_context: FormReplyContext):
        return passed_context.form_id == "test_form"

    activity.matches = dummy_matcher

    context._form_id = "test_form"
    assert activity.matches(context)

    context._form_id = "form_test"
    assert not activity.matches(context)


def test_before_matcher(activity, context):
    activity.before_matcher(context)

    assert context.form_id == "test_form"
    assert context.get_form_value("key") == "value"
    assert context.get_form_value("non_existing_key") is None
