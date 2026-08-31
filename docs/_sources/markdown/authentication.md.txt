# Authentication
The Symphony BDK authentication API allows developers to authenticate their bots and apps using RSA authentication mode.

The following sections will explain you:
- how to authenticate your bot service account
- how to authenticate your app to use OBO (On Behalf Of) authentication

## Bot authentication

In this section we will see how to authenticate a bot service account. You will notice that everything has to be done
through your BDK `config.yaml`, making your code completely agnostic to authentication modes (RSA or certificate).

Only one of certificate or RSA authentication should be configured in one BDK `config.yaml`. If both of them are
provided, an `AuthInitializationError` will be thrown when you try to authenticate to the bot service account.

### Bot authentication using RSA
In this section we will see how to authenticate a bot service account using RSA authentication.

> Read more about RSA authentication [here](https://docs.developers.symphony.com/building-bots-on-symphony/authentication/rsa-authentication)

Required `config.yaml` setup:
```yaml
host: acme.symphony.com
bot:
    username: bot-username
    privateKey:
      path: /path/to/rsa/private-key.pem
```

### Bot authentication using Client Certificate
> Read more about Client Certificate authentication [here](https://docs.developers.symphony.com/building-bots-on-symphony/authentication/certificate-authentication)

Required `config.yaml` setup:
```yaml
host: acme.symphony.com
bot:
    username: bot-username
    certificate:
      path: /path/to/certificate.pem
```
To know more about the format of the certificate file, check [SSLContext.load_cert_chain](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain).
The certificate path will be passed to the `certfile` parameter of the `load_cert_chain_method`. We do not pass anything
to `keyfile` and `password` parameters, which means certificate and decrypted private key should be put in the same file.

The certificate path should lead to a single file in PEM format containing the certificate and the decrypted private key. 
We do not support password encrypted private keys.

Alternatively, if you have another key format, you can use the OpenSSL Command line tool to convert it to `.pem` format:
```bash
openssl pkcs12 -in certificate.{p12, pfx} -out certificate.pem -nodes
```

### Bot authentication deep-dive
The code snippet below explains how to manually retrieve your bot authentication session. However, note that by default
those operations are done behind the scene through the `SymphonyBdk` entry point.

```python
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
```

### Authentication using private key content
Instead of configuring the path of RSA private key config file, you can also authenticate the bot 
and extension app by using directly the private key or certificate content. This feature is useful when either 
RSA private key is fetched from an external secrets storage. The code snippet below will give you 
an example showing how to set directly the private key content to the Bdk configuration for authenticating the bot.
````python
import asyncio
import logging

from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    # loading configuration
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    # update private key with content
    private_key_string = '-----BEGIN RSA PRIVATE KEY-----'
    config.bot.private_key.content = private_key_string
                                      
    async with SymphonyBdk(config) as bdk:
        auth_session = bdk.bot_session()
        logging.info(await auth_session.key_manager_token)
        logging.info(await auth_session.session_token)
````

### Multiple bot instances
By design, the `SymphonyBdk` object contains a single bot session. However, you might want to create an application that
has to handle multiple bot sessions, potentially using different authentication modes. This is possible by creating
multiple instances of `SymphonyBdk` using different configurations:
```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk

async def run():
    config_a = BdkConfigLoader.load_from_symphony_dir("config_a.yaml")
    config_b = BdkConfigLoader.load_from_symphony_dir("config_b.yaml")

    async with SymphonyBdk(config_a) as bdk_a, SymphonyBdk(config_b) as bdk_b:
        # use your two service accounts
```

## App authentication
Application authentication is completely optional but remains required if you want to use OBO.

### Using RSA
Required `config.yaml` setup:
```yaml
host: acme.symphony.com
app:
    appId: app-id
    privateKey:
      path: /path/to/rsa/private-key.pem
```

### Using Client Certificate
> Read more about certificate authentication [here](https://docs.developers.symphony.com/building-bots-on-symphony/authentication/certificate-authentication)

Required `config.yaml` setup: 
```yaml
host: acme.symphony.com
app:
    appId: app-id
    certificate:
      path: /path/to/certificate.pem
```

To know more about the format of the certificate file, check [SSLContext.load_cert_chain](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_cert_chain).
The certificate path will be passed to the `certfile` parameter of the `load_cert_chain_method`. We do not pass anything
to `keyfile` and `password` parameters, which means certificate and decrypted private key should be put in the same file.

### Circle Of Trust
> Read more about Circle Of Trust
> [here](https://docs.developers.symphony.com/building-extension-applications-on-symphony/app-authentication/circle-of-trust-authentication)

```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        ext_app_authenticator = bdk.app_authenticator()

        app_auth = await ext_app_authenticator.authenticate_extension_app("appToken")
        ta = app_auth.app_token
        ts = app_auth.symphony_token

        assert await ext_app_authenticator.is_token_pair_valid(ta, ts)
```

In order to have a fully working extension app, your extension app backend will have to expose the following endpoints:
* a POST authentication endpoint (e.g. POST /authenticate) which will we generate an app token, call
  `await ext_app_authenticator.authenticate_extension_app("appToken")` and return the result.
* a POST validate tokens endpoint (e.g. POST /tokens) which will validate the `appToken` and `symphonyToken` passed in
  the body is valid according to the result of
  `await ext_app_authenticator.is_token_pair_valid(app_token, symphony_token)`.
* a POST validate jwt endpoint (e.g. POST /jwt) which will validate a jwt passed in the `jwt` field of the body and will
  return the result of `await ext_app_authenticator.validate_jwt(jwt)`.

### OBO (On Behalf Of) authentication
> Read more about OBO authentication [here](https://docs.developers.symphony.com/building-extension-applications-on-symphony/app-authentication/obo-authentication)

The following example shows how to retrieve OBO sessions using `username` (type `str`) or `user_id` (type `int`)
and to call services which have OBO endpoints (users, streams, connections and messages so far):

```python
from symphony.bdk.core.config.loader import BdkConfigLoader
from symphony.bdk.core.symphony_bdk import SymphonyBdk


async def run():
    config = BdkConfigLoader.load_from_symphony_dir("config.yaml")
    async with SymphonyBdk(config) as bdk:
        obo_auth_session = bdk.obo(username="username")
        async with bdk.obo_services(obo_auth_session) as obo_services:
            obo_services.messages().send_message("stream_id", "<messageML>Hello on behalf of user!</messageML>")
```

### BDK running without Bot username (service account) configured

When the bot `username` (service account) is not configured in the Bdk configuration, the bot project will be still
runnable but only in the OBO mode if the app authentication is well-configured.

The `config.yaml` requires at least the application configuration:

```yaml
host: acme.symphony.com
app:
    appId: app-id
    privateKey:
      path: /path/to/private-key.pem
```

If users still try to access to Bdk services directly from `SymphonyBdk` facade object, a `BotNotConfiguredError`
will be thrown.

The example in [part above](#obo-on-behalf-of-authentication) shows how a bot project works without bot `username`
configured.
