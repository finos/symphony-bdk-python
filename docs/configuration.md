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
3. Load configuration from the Symphony directory. The Symphony directory is located under `.symphony` folder in your home directory 
    . It can be useful when you don't want to share your own Symphony credentials within your project codebase

