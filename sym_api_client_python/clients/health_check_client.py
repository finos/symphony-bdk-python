import logging

from .api_client import APIClient


class HealthCheckClient(APIClient):
    def __init__(self, bot_client):
        self.bot_client = bot_client

    def get_health_check(self, show_firehose_errors=False):
        logging.debug('HealthCheckClient/get_health_check()')
        params = {'showFirehoseErrors': show_firehose_errors}
        url = '/agent/v2/HealthCheck'
        return self.bot_client.execute_rest_call('GET', url, params=params)

    def ensure_all_services_up(self, check_firehose=False, fields_to_check=None):
        logging.debug('HealthCheckClient/ensure_all_services_up()')
        # This list would have to be updated if new fields became available in the health check
        if fields_to_check is None:
            fields_to_check = [
                'podConnectivity',
                'keyManagerConnectivity',
                'encryptDecryptSuccess',
                'agentServiceUser',
                'ceServiceUser',
            ]
        if check_firehose:
            fields_to_check.append('firehoseConnectivity')

        health_check = self.get_health_check(check_firehose)

        logging.debug(health_check)

        functioning = [ health_check[field] for field in fields_to_check ]
        if not all(functioning):
            problems = [fields_to_check[i] for i,v in enumerate(functioning) if not v]
            raise RuntimeError(f"Not all services available: {problems}")
            

