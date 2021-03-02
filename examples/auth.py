import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
        logging.info("Obo example:")
        obo_auth_session = bdk.obo(username="username")
        logging.info(await obo_auth_session.session_token)

        # update private key and certificate
        private_key_string = '-----BEGIN RSA PRIVATE KEY-----\n'\
                             'zI2OZtdb8fu/xl7itIAOzKLFg3mhAQtCpXLxGYwm4SDOoxAz4yTQJ+jjS+cxqh74\n'\
                             'C7zqk+Tj9H0ANN+XLenyYlNO737Hja6g3xrD1Pd5cWgp47N1OToQEiucrcqVu7ns\n'\
                             'ZS5cuoJd+hOuPYZasZrQBv03hp+t4DGPRNFhHIRbqkxxZo3MC6R13cqdTyhRsewG\n'\
                             '...\n'\
                             '-----END RSA PRIVATE KEY-----'

        certificate_string = '-----BEGIN CERTIFICATE-----\n' \
                             'ggEBAL5Z8cEbWs5jnXxWneP1nO9Hu6oCWErdK4aPDb/otarsMF0ZYmWKR3Urr1Fe\n' \
                             'rTadMDHOFki40JPibkUxTmW0IfSV4Hw3QOordMtMyhLfGes9f45VrkSH74VjfsPa\n' \
                             '...\n'\
                             '-----END CERTIFICATE-----'

        # update private key
        config.setBotConfig(private_key_content=private_key_string)

        # update certificate
        config.setBotConfig(certificate_content=certificate_string)

        async with SymphonyBdk(config) as bdk:
            auth_session = bdk.bot_session()
            logging.info(await auth_session.key_manager_token)
            logging.info(await auth_session.session_token)

logging.basicConfig(level=logging.DEBUG)
asyncio.run(run())
