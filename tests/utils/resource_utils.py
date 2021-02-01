from pathlib import Path
import json
from types import SimpleNamespace


def get_resource_filepath(relative_path, as_text=True):
    resources_path = Path(__file__).parent / "../resources"
    resource_path = resources_path / relative_path
    if as_text:
        return str(resource_path.resolve())
    else:
        return resource_path.resolve()


def get_resource_content(relative_path):
    return get_resource_filepath(relative_path, as_text=False).read_text()


def object_from_json(json_content):
    return json.loads(json_content, object_hook=lambda d: SimpleNamespace(**d))


def object_from_json_relative_path(relative_path):
    return object_from_json(get_resource_content(relative_path))


def get_config_resource_filepath(relative_path, as_text=True):
    """Gets the absolute path of the resource

    :param relative_path: str relative path of the resources at "test/resources/"
    :param as_text: bool  return a string path if True,  a pathlib.Path object otherwise
    :return: the absolute path of the specified resource
    """
    resources_path = Path(__file__).parent / "../resources/config"
    resource_path = resources_path / relative_path
    if as_text:
        return str(resource_path.resolve())
    else:
        return resource_path.resolve()
