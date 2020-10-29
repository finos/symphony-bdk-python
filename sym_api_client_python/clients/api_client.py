import logging

import aiohttp
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from ..exceptions.APIClientErrorException import APIClientErrorException
from ..exceptions.DatafeedExpiredException import DatafeedExpiredException
from ..exceptions.ForbiddenException import ForbiddenException
from ..exceptions.ServerErrorException import ServerErrorException
from ..exceptions.UnauthorizedException import UnauthorizedException


# error handling class --> take status code and raise appropriate exceptions
# this class acts as a parent class to each of the other client class.
# each child class extends error handling functionality


class APIClient:

    def __init__(self, bot_client):
        self.bot_client = bot_client

    def make_mulitpart_form(self, fields, aio=False):
        """Create a multipart form to be used across the Symphony API, that works for both requests
        and the asynchronous aiohttp. Requests basically uses requests-toolbelt, but it's a little
        bit more involved for aiohttp. The output of this is expected to be passed to either
        execute_rest_request or execute_rest_request_async depending whether aio was true"""

        if aio:
            # This appears to be the canonical way to use aiohttp to pass mulipart data into the API
            # in the same way that MultipartEncoder does for Requests.
            # aiohttp.FormData does appear to work because of the way the Symphony API demands a boundary
            # in the header. aiohttp.MultipartWriter.append_form doesn't appear to work because it
            # encodes as a application/x-www-form-urlencoded that Symphony doesn't appear to like for
            # attachments
            with aiohttp.MultipartWriter("form-data") as data:
                for k, v in fields.items():
                    if len(v) == 1:
                        part = data.append(v)
                        part.set_content_disposition("form-data", name=k)
                    if len(v) == 3:
                        filename, file_object, content_type = v
                        part = data.append(file_object, {'Content-Type': content_type})
                        part.set_content_disposition('form-data', name=k, filename=filename)

            headers = {
                'Content-Type': 'multipart/form-data; boundary=' + data.boundary
            }

        else:
            data = MultipartEncoder(
                fields=fields
            )
            headers = {
                'Content-Type': data.content_type
            }

        return {"data": data, "headers": headers}

    def handle_error(self, response, bot_client, error_json=None, text=None):
        logging.debug('api_client/handle_error() function started')
        _error_field = "message"
        if isinstance(response, requests.Response):
            status = response.status_code
        else:
            # The assumption is that it's an aiohttp response from an async request
            status = response.status

        try:
            if error_json is not None:
                try:
                    err_message = error_json[_error_field]
                except KeyError:
                    if text is not None:
                        err_message = text
                    else:
                        err_message = ""
            elif text is not None:
                err_message = text
            else:
                err_message = ""

        except Exception:
            logging.error("Unable to parse error message: {}".format(text))
            err_message = ""

        if status == 400 and 'Could not find a datafeed with the' in err_message:
            logging.debug('datafeed expired, start_datafeed()')
            raise DatafeedExpiredException()

        elif status == 401:
            logging.debug('api_client()/handling 401 error')
            bot_client.reauth_client()
            logging.debug('api_client()/successfully reauthenticated')
            raise UnauthorizedException(
                'User, unauthorized, refreshing tokens: {}'
                    .format(status))
        elif status == 403:
            raise ForbiddenException(
                'Forbidden: Caller lacks necessary entitlement: {}'
                    .format(status))
        elif status == 405:
            logging.debug('Handling 405 error')
            raise ForbiddenException(
                'Method Not Allowed: The method received in the request-line is known by the origin server but not supported by the target resource: {}'
                    .format(status))

        # Response dict is a bit of an information overload, could consider trimming it
        elif 400 <= status < 500:

            raise APIClientErrorException('Client Error Occurred: {}. Response contents: {}'
                                          .format(err_message, response.__dict__))

        elif status >= 500:
            raise ServerErrorException(
                'Server Error Exception: {}, {}'
                    .format(status, err_message))
        else:
            # This shouldn't happen
            raise RuntimeError("Unhandled error: {}".format(response.__dict__))
