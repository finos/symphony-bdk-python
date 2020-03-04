import setuptools


def readme():
    with open('README.md') as f:
        return f.read()

test_dependencies = [
    'pytest',
]

# This means dependencies for testing can be installed with:
# pip install .[test]
# See this Stackoverflow answer for details
# https://stackoverflow.com/a/41398850
extras = {
    "test": test_dependencies,
}

setuptools.setup(
    name="sym_api_client_python",

    version="1.1.0",
    author="Symphony Platform Solutions",
    author_email="platformsolutions@symphony.com",
    description="Symphony REST API - Python Client",
    long_description=readme(),
    long_description_content_type='text/markdown',
    url="https://github.com/SymphonyPlatformSolutions/"
        "symphony-api-client-python",
    packages=setuptools.find_packages(),
    install_requires=[
        'aiohttp',
        'aioresponses>=0.6.1',
        'pyOpenSSL',
        'rsa',
        'requests',
        'python-jose',
        'urllib3<1.25,>=1.21.',
        'python-json-logger==0.1.11',
        'beautifulsoup4==4.8.0',
        'Jinja2==2.10.1',
        'requests_pkcs12==1.4',
        'requests-toolbelt==0.9.1',
        'requests-mock>=1.7.0',
        'yattag==1.12.2'
    ],
    extras_require=extras,
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
