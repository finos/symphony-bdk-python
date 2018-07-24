import tempfile
from OpenSSL import crypto

class Crypt():

    def __init__(self, symphony_p12, symphony_pwd):
        self.p12 = symphony_p12
        self.pwd = symphony_pwd

    def write_tmpfile(self, string):
        fd, path = tempfile.mkstemp()
        filehandle = open(path, 'wb')
        filehandle.write(string)
        filehandle.close()
        return path

    def p12parse(self):
        ''' parse p12 cert and get the cert / priv key for requests module '''
        # open it, using password. Supply/read your own from stdin.
        p12 = crypto.load_pkcs12(open(self.p12, 'rb').read(), self.pwd)
        # grab the certs / keys
        p12cert = p12.get_certificate()     # (signed) certificate object
        p12private = p12.get_privatekey()      # private key.
        # dump private key and cert
        symphony_key = crypto.dump_privatekey(crypto.FILETYPE_PEM, p12private)
        symphony_crt = crypto.dump_certificate(crypto.FILETYPE_PEM, p12cert)
        # write tmpfiles
        crtpath = self.write_tmpfile(symphony_crt)
        keypath = self.write_tmpfile(symphony_key)
        # return cert and privkey
        return crtpath, keypath
