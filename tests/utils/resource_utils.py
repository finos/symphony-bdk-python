import json
from pathlib import Path

from symphony.bdk.gen.api_client import validate_and_convert_types
from symphony.bdk.gen.configuration import Configuration


def get_resource_filepath(relative_path, as_text=True):
    resources_path = Path(__file__).parent / "../resources"
    resource_path = resources_path / relative_path
    if as_text:
        return str(resource_path.resolve())
    return resource_path.resolve()


def get_resource_content(relative_path):
    return get_resource_filepath(relative_path, as_text=False).read_text()


def get_deserialized_object_from_resource(return_type, resource_path):
    payload = get_resource_content(resource_path)
    return deserialize_object(return_type, payload)


def deserialize_object(model, payload):
    """Deserializes the passed payload to an instance of the specified model
    Disregards unknown fields is

    :param model: OpenApi generated model
    :param payload: json payload to be deserialized
    :return: Instance of the model
    """
    try:
        test_data = json.loads(payload)
    except json.JSONDecodeError:
        test_data = payload
    return validate_and_convert_types(
        input_value=test_data,
        required_types_mixed=(model,),
        path_to_item=["test_data"],
        spec_property_naming=True,
        _check_type=True,
        configuration=Configuration(discard_unknown_keys=True),
    )


def get_config_resource_filepath(relative_path):
    """Gets the absolute path of the resource

    :param relative_path: str relative path of the resources at "test/resources/"
    :return: the absolute path of the specified resource
    """
    resources_path = Path(__file__).parent / "../resources/config"
    resource_path = resources_path / relative_path
    return str(resource_path.resolve())
