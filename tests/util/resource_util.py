import os

def get_resource_filepath(path_relative_to_resources):
	filepath = os.path.join(os.path.dirname(__file__), '../resources/', path_relative_to_resources)
	return os.path.normpath(filepath)