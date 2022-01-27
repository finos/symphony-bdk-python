# Configuration

The BDK configuration is one of the most essential feature of the Symphony BDK which allows developers to configure
their bot environment.

## Minimal configuration example
The minimal configuration file that can be provided look like:
```yaml
host: mypod.symphony.com                                     # (1)

bot:
    username: bot-username                                  # (2)
    privateKey:
      path: /path/to/bot/rsa-private-key.pem                # (3)

app:
    appId: app-id                                           # (4)
    privateKey:
      path: /path/to/bot/rsa-private-key.pem                # (5)
```
1. hostname of your Symphony pod environment
2. your bot (or service account) username as configured in your pod admin console (https://mypod.symphony.com/admin-console)
3. your bot RSA private key according to the RSA public key upload in your pod admin console (https://mypod.symphony.com/admin-console)
4. the app id of your extension application configured in your pod admin console.
5. your RSA private key to authenticate the extension application according to the RSA public key associated with your extension application.

## How to load configuration
The Symphony BDK provides a single way to configure your bot environment.

```python
from symphony.bdk.core.config.loader import BdkConfigLoader

config_1 = BdkConfigLoader.load_from_file("/absolute/path/to/config.yaml")  # 1

config_2 = BdkConfigLoader.load_from_content(config_content_as_string)  # 2

config_3 = BdkConfigLoader.load_from_symphony_dir("config.yaml")  # 3
```
1. Load configuration from a file
2. Load configuration from a string object
3. Load configuration from the Symphony directory. The Symphony directory is located under `.symphony` folder in your
   home directory. It can be useful when you don't want to share your own Symphony credentials within your project
   codebase

## Full configuration example
```yaml
scheme: https
host: localhost.symphony.com
port: 8443
defaultHeaders:
  Connection: Keep-Alive
  Keep-Alive: timeout=5, max=1000

proxy:
  host: proxy.symphony.com
  port: 1234
  username: proxyuser
  password: proxypassword

pod:
  host: dev.symphony.com
  port: 443

agent:
   host: dev-agent.symphony.com
   port: 5678
   proxy:
     host: agent-proxy
     port: 3396

keyManager:
  host: dev-key.symphony.com
  port: 8444
  defaultHeaders:
    Connection: Keep-Alive
    Keep-Alive: close

sessionAuth:
  host: dev-session.symphony.com
  port: 8444

ssl:
  trustStore:
    path: /path/to/truststore.pem

bot:
  username: bot-name
  privateKey:
    path: /path/to/bot/rsa-private-key.pem

app:
  appId: app-id
  certificate:
    path: path/to/app-certificate.pem

datafeed:
  version: v2
  retry:
    maxAttempts: 6
    initialIntervalMillis: 2000
    multiplier: 1.5
    maxIntervalMillis: 10000

retry:
  maxAttempts: 6 # set '-1' for an infinite number of attempts, default value is '10'
  initialIntervalMillis: 2000
  multiplier: 1.5
  maxIntervalMillis: 10000
```

### Configuration structure

The BDK configuration now includes the following properties:
- The BDK configuration can contain the global properties for `host`, `port`, `context` and `scheme`.
These global properties can be used by the client configuration by default or can be overridden if
user specify the dedicated `host`, `port`, `context`, `scheme` inside the client configuration.
- `proxy` contains proxy related information. This field is optional.
If set, it will use the provided `host` (mandatory), `port` (mandatory), `username` and `password`.
It can be overridden in each of the `pod`, `agent`, `keyManager` and `sessionAuth` fields.
For instance, if you want a proxy for the agent only:
```yaml
host: acme.symphony.com

agent:
  host: agent.symphony.com
  proxy:
    host: proxy.symphony.com
    port: 1234
    username: proxyuser
    password: proxypassword

bot:
  username: bot-name
  privateKey:
    path: /path/to/bot/rsa-private-key.pem

datafeed:
  version: v2
```
- `defaultHeaders` contains the default headers to be sent along with each request.
  It can be overridden in each of the `pod`, `agent`, `keyManager` and `sessionAuth` fields.
- `pod` contains information like host, port, scheme, context, proxy... of the pod on which
the service account using by the bot is created.
- `agent` contains information like host, port, scheme, context, proxy... of the agent which
the bot connects to.
- `keyManager` contains information like host, port, scheme, context, proxy... of the key
manager which manages the key token of the bot.
- `ssl` contains the path to a file of concatenated CA certificates in PEM format. As we are using python SSL library
  under the hood, you can check
  [ssl lib documentation on certificates](https://docs.python.org/3/library/ssl.html#certificates) for more information.

  To fetch the cert file in pem format, you can run the following openssl command: `openssl s_client -connect <host>:<port> -showcerts > cert.pem`
  If not specified, the BDK will load default system certificates using [SSLContext.load_default_certs](https://docs.python.org/3/library/ssl.html#ssl.SSLContext.load_default_certs).
- `bot` contains information about the bot like the username, the private key for authenticating the service account
  on pod.
- `app` contains information about the extension app that the bot will use like
the appId, the private key or certificate for authenticating the extension app.
- `datafeed` contains information about the datafeed service that the bot will use for the `DatafeedLoop` service.
If the version field is configured to `v2`, the datafeed service v2 will be used. Otherwise, the datafeed service v1
will be used by default.
- `retry` contains information for retry mechanism to be used by the bot.

#### Retry Configuration
The retry mechanism used by the bot will be configured by these following properties:
- `maxAttempts`: maximum number of retry attempts that the bot will make. Setting it to `-1` is equivalent to an infinite number of attempts
- `multiplier`: after each attempt, the interval between two attempts will be multiplied by
this factor. (Exponential backoff strategy)
- `initialIntervalMillis`: the interval between the initial two attempts in milliseconds.
- `maxIntervalMillis`: the limit of the interval between two attempts. For example: if the
current interval is 1000 millis, multiplier is 2.0 and the maxIntervalMillis is 1500 millis,
then the interval for next retry will be 1500 millis.

Each bot will have a global retry configuration to be used in every service with the following
default value:
- `maxAttempts`: 10
- `initialIntervalMillis`: 500
- `multiplier`: 2
- `maxIntervalMillis`: 300000 (5 mins)
