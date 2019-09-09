

def convert_to_dict(obj):
      """
      A function takes in a custom object and returns a dictionary representation of the object.
      This dict representation includes meta data such as the object's module and class names.
      """

      #  Populate the dictionary with object meta data
      obj_dict = {}

      #  Populate the dictionary with object properties
      obj_dict.update(obj.__dict__)

      return obj_dict
