import json
from pathlib import Path

from typing import get_origin, get_args, List


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
    """Deserializes the passed payload to an instance of the specified model.

    :param model: The model to deserialize to (Pydantic model, primitive type, or List[...] of those).
    :param payload: JSON payload to be deserialized.
    :return: Instance of the model
    """
    # If the model is a List[...] type
    origin = get_origin(model)
    if origin in (list, List):
        (inner_model,) = get_args(model)

        # Ensure payload is parsed JSON list
        if isinstance(payload, str):
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                raise ValueError("Expected JSON array for List[...] model")
        else:
            data = payload

        if not isinstance(data, list):
            raise ValueError(f"Expected list for {model}, got {type(data)}")

        return [
            deserialize_object(inner_model, item)  # recursively call
            for item in data
        ]

    # Handle single objects (Pydantic models)
    if hasattr(model, "from_json"):
        if isinstance(payload, str):
            return model.from_json(payload)
        else:
            return model.model_validate(payload)  # Pydantic v2 compatibility

    # Fallback for primitive types
    if isinstance(payload, str):
        try:
            data = json.loads(payload)
        except json.JSONDecodeError:
            data = payload
    else:
        data = payload

    return model(data)


def get_config_resource_filepath(relative_path):
    """Gets the absolute path of the resource

    :param relative_path: str relative path of the resources at "test/resources/"
    :return: the absolute path of the specified resource
    """
    resources_path = Path(__file__).parent / "../resources/config"
    resource_path = resources_path / relative_path
    return str(resource_path.resolve())
