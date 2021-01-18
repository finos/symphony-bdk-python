from pathlib import Path


def get_resource_filepath(relative_path):
    resources_path = Path(__file__) / "../resources"
    return resources_path / relative_path


def get_config_resource_filepath(relative_path, as_text=True):
    resources_path = Path(__file__).parent / "../resources/config"
    resource_path = resources_path / relative_path
    if as_text:
        return str(resource_path.resolve())
    else:
        return resource_path.resolve()
