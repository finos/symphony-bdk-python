"""
Fixtures defined here will be shared among all tests in the test suite.
"""

import datetime

import pytest

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509 import NameOID


@pytest.fixture(name="root_key", scope="session")  # the fixture will be created only once for entire test session.
def fixture_root_key():
    return rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend())


@pytest.fixture(name="rsa_key", scope="session")
def fixture_rsa_key(root_key):
    return root_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()).decode("utf-8")


@pytest.fixture(name="certificate", scope="session")
def fixture_certificate(root_key):
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, u"commonName")])
    now = datetime.datetime.utcnow()
    cert = x509.CertificateBuilder() \
        .subject_name(subject) \
        .issuer_name(issuer) \
        .public_key(root_key.public_key()) \
        .serial_number(x509.random_serial_number()) \
        .not_valid_before(now) \
        .not_valid_after(now + datetime.timedelta(days=30)) \
        .sign(root_key, hashes.SHA512(), default_backend())
    return cert.public_bytes(encoding=serialization.Encoding.PEM).decode("utf-8")
