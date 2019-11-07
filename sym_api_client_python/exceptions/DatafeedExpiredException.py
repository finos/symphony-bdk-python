class DatafeedExpiredException(Exception):
    """This exception represents the response below from the API that occurs periodically
    when a datafeed has expired. It should be handled by creating a new datafeed and 
    reading from there"""
    pass
