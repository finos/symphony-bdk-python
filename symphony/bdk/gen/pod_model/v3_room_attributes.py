"""
    Pod API

    This document refers to Symphony API calls that do not need encryption or decryption of content.  - sessionToken can be obtained by calling the authenticationAPI on the symphony back end and the key manager respectively. Refer to the methods described in authenticatorAPI.yaml. - Actions are defined to be atomic, ie will succeed in their entirety or fail and have changed nothing. - If it returns a 40X status then it will have made no change to the system even if ome subset of the request would have succeeded. - If this contract cannot be met for any reason then this is an error and the response code will be 50X.   # noqa: E501

    The version of the OpenAPI document: 20.10.0
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401
from typing import List

from symphony.bdk.gen.model_utils import (  # noqa: F401
    ApiTypeError,
    ModelComposed,
    ModelNormal,
    ModelSimple,
    cached_property,
    change_keys_js_to_python,
    convert_js_args_to_python_args,
    date,
    datetime,
    file_type,
    none_type,
    validate_get_composed_info,
)

from symphony.bdk.gen.pod_model.room_tag import RoomTag
globals()['RoomTag'] = RoomTag


class V3RoomAttributes(ModelNormal):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.

    Attributes:
      allowed_values (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          with a capitalized key describing the allowed value and an allowed
          value. These dicts store the allowed enum values.
      attribute_map (dict): The key is attribute name
          and the value is json key in definition.
      discriminator_value_class_map (dict): A dict to go from the discriminator
          variable value to the discriminator class name.
      validations (dict): The key is the tuple path to the attribute
          and the for var_name this is (var_name,). The value is a dict
          that stores validations for max_length, min_length, max_items,
          min_items, exclusive_maximum, inclusive_maximum, exclusive_minimum,
          inclusive_minimum, and regex.
      additional_properties_type (tuple): A tuple of classes accepted
          as additional properties values.
    """

    allowed_values = {
    }

    validations = {
    }

    additional_properties_type = None

    _nullable = False

    @cached_property
    def openapi_types():
        """
        This must be a method because a pod_model may have properties that are
        of type self, this must run after the class is loaded

        Returns
            openapi_types (dict): The key is attribute name
                and the value is attribute type.
        """
        return {
            'name': (str, none_type),  # noqa: E501
            'keywords': ([RoomTag], none_type),  # noqa: E501
            'description': (str, none_type),  # noqa: E501
            'members_can_invite': (bool, none_type),  # noqa: E501
            'discoverable': (bool, none_type),  # noqa: E501
            'public': (bool, none_type),  # noqa: E501
            'read_only': (bool, none_type),  # noqa: E501
            'copy_protected': (bool, none_type),  # noqa: E501
            'cross_pod': (bool, none_type),  # noqa: E501
            'view_history': (bool, none_type),  # noqa: E501
            'multi_lateral_room': (bool, none_type),  # noqa: E501
            'scheduled_meeting': (bool, none_type),  # noqa: E501
            'sub_type': (str, none_type),  # noqa: E501
        }

    @cached_property
    def discriminator():
        return None


    attribute_map = {
        'name': 'name',  # noqa: E501
        'keywords': 'keywords',  # noqa: E501
        'description': 'description',  # noqa: E501
        'members_can_invite': 'membersCanInvite',  # noqa: E501
        'discoverable': 'discoverable',  # noqa: E501
        'public': 'public',  # noqa: E501
        'read_only': 'readOnly',  # noqa: E501
        'copy_protected': 'copyProtected',  # noqa: E501
        'cross_pod': 'crossPod',  # noqa: E501
        'view_history': 'viewHistory',  # noqa: E501
        'multi_lateral_room': 'multiLateralRoom',  # noqa: E501
        'scheduled_meeting': 'scheduledMeeting',  # noqa: E501
        'sub_type': 'subType',  # noqa: E501
    }

    _composed_schemas = {}

    required_properties = set([
        '_data_store',
        '_check_type',
        '_spec_property_naming',
        '_path_to_item',
        '_configuration',
        '_visited_composed_classes',
    ])

    @convert_js_args_to_python_args
    def __init__(self, name: str = None, keywords: List[RoomTag] = None, description: str = None, members_can_invite: bool = None, discoverable: bool = None, public: bool = None, read_only: bool = None, copy_protected: bool = None, cross_pod: bool = None, view_history: bool = None, multi_lateral_room: bool = None, scheduled_meeting: bool = None, sub_type: str = None, *args, **kwargs):  # noqa: E501
        """V3RoomAttributes - a pod_model defined in OpenAPI

        Keyword Args:
            _check_type (bool): if True, values for parameters in openapi_types
                                will be type checked and a TypeError will be
                                raised if the wrong type is input.
                                Defaults to True
            _path_to_item (tuple/list): This is a list of keys or values to
                                drill down to the pod_model in received_data
                                when deserializing a response
            _spec_property_naming (bool): True if the variable names in the input data
                                are serialized names, as specified in the OpenAPI document.
                                False if the variable names in the input data
                                are pythonic names, e.g. snake case (default)
            _configuration (Configuration): the instance to use when
                                deserializing a file_type parameter.
                                If passed, type conversion is attempted
                                If omitted no type conversion is done.
            _visited_composed_classes (tuple): This stores a tuple of
                                classes that we have traveled through so that
                                if we see that class again we will not use its
                                discriminator again.
                                When traveling through a discriminator, the
                                composed schema that is
                                is traveled through is added to this set.
                                For example if Animal has a discriminator
                                petType and we pass in "Dog", and the class Dog
                                allOf includes Animal, we move through Animal
                                once using the discriminator, and pick Dog.
                                Then in Dog, we will make an instance of the
                                Animal class but this time we won't travel
                                through its discriminator because we passed in
                                _visited_composed_classes = (Animal,)
            name (str): Room name.. [optional]  # noqa: E501
            keywords ([RoomTag]): Keywords for search to use to find this room. [optional]  # noqa: E501
            description (str): Room description.. [optional]  # noqa: E501
            members_can_invite (bool): If true, any chatroom participant can add new participants. If false, only owners can add new participants.. [optional]  # noqa: E501
            discoverable (bool): If true, this chatroom (name, description and messages) can be searched and listed by non-participants. If false, only participants can search this room.. [optional]  # noqa: E501
            public (bool): If true, this is a public chatroom. IF false, a private chatroom.. [optional]  # noqa: E501
            read_only (bool): If true, only stream owners can send messages.. [optional]  # noqa: E501
            copy_protected (bool): If true, clients disable the clipboard copy for content in this stream.. [optional]  # noqa: E501
            cross_pod (bool): If true, this room is a cross pod room. [optional]  # noqa: E501
            view_history (bool): If true, new members can view the room chat history of the room.. [optional]  # noqa: E501
            multi_lateral_room (bool): If true, this is a multi lateral room where we can find users belonging to more than 2 companies.. [optional]  # noqa: E501
            scheduled_meeting (bool): If true, this room is for a scheduled meeting.. [optional]  # noqa: E501
            sub_type (str): Possible value EMAIL (indicate this room will be used for Email Integration). [optional]  # noqa: E501
        """

        _check_type = kwargs.pop('_check_type', True)
        _spec_property_naming = kwargs.pop('_spec_property_naming', False)
        _path_to_item = kwargs.pop('_path_to_item', ())
        _configuration = kwargs.pop('_configuration', None)
        _visited_composed_classes = kwargs.pop('_visited_composed_classes', ())

        if args:
            raise ApiTypeError(
                "Invalid positional arguments=%s passed to %s. Remove those invalid positional arguments." % (
                    args,
                    self.__class__.__name__,
                ),
                path_to_item=_path_to_item,
                valid_classes=(self.__class__,),
            )

        self._data_store = {}
        self._check_type = _check_type
        self._spec_property_naming = _spec_property_naming
        self._path_to_item = _path_to_item
        self._configuration = _configuration
        self._visited_composed_classes = _visited_composed_classes + (self.__class__,)

        self.name: str = name
        self.keywords: List[RoomTag] = keywords
        self.description: str = description
        self.members_can_invite: bool = members_can_invite
        self.discoverable: bool = discoverable
        self.public: bool = public
        self.read_only: bool = read_only
        self.copy_protected: bool = copy_protected
        self.cross_pod: bool = cross_pod
        self.view_history: bool = view_history
        self.multi_lateral_room: bool = multi_lateral_room
        self.scheduled_meeting: bool = scheduled_meeting
        self.sub_type: str = sub_type

        for var_name, var_value in kwargs.items():
            if var_name not in self.attribute_map and \
                        self._configuration is not None and \
                        self._configuration.discard_unknown_keys and \
                        self.additional_properties_type is None:
                # discard variable.
                continue
            setattr(self, var_name, var_value)
