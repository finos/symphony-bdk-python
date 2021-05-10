# Frequently Asked Questions

## How do I solve SSLCertVerificationError when running the bot?

The following stack trace:

```
File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/site-packages/aiohttp/connector.py", line 969, in _wrap_create_connection
return await self._loop.create_connection(*args, **kwargs) # type: ignore # noqa

File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/asyncio/base_events.py", line 1050, in create_connection
transport, protocol = await self._create_connection_transport(

File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/asyncio/base_events.py", line 1080, in _create_connection_transport
await waiter

File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/asyncio/sslproto.py", line 529, in data_received
ssldata, appdata = self._sslpipe.feed_ssldata(data)

File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/asyncio/sslproto.py", line 189, in feed_ssldata
self._sslobj.do_handshake()

File "/Library/Frameworks/Python.framework/Versions/3.8/lib/python3.8/ssl.py", line 944, in do_handshake
self._sslobj.do_handshake()

ssl.SSLCertVerificationError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self signed certificate in certificate chain (_ssl.c:1123)
```

means the server (e.g. pod or agent) certificate is not recognized as a valid one.

1. If you are running MacOS X, the cause may be due to a bug when installing python on mac as documented in this
   [stackoverflow issue](https://stackoverflow.com/questions/42098126/mac-osx-python-ssl-sslerror-ssl-certificate-verify-failed-certificate-verify).
   If so, try to run `bash /Applications/Python*/Install\ Certificates.command` and rerun your bot. If you are not able 
   to locate `Certificate.command`, try running script mentioned [here](https://stackoverflow.com/a/61142526).

2. If issue persists or if you are not running MacOS X, the certificate is probably self-signed or not present in your
   OS keychain. If so, the recommended way to solve this is to use valid certificates signed with a trusted CA.
   Otherwise, you will have to add the certificates in your OS keychain or add it to the bot configuration.

To do so, fetch the server certificate by running:
```
openssl s_client -connect <pod host>:<pod port> -showcerts > cert.pem
```

If you use different hosts and ports for the `agent`, `keyManager` and `sessionAuth`, you will have to repeat the
command above with the specific hosts and ports and append all the certificates to the same file.

Then, either add the certificate to your OS keychain or add it to your configuration:

```yaml
ssl:
  trustStore:
    path: /path/to/cert.pem
```

