import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


setuptools.setup(
    name="sym_api_client_python",

    version="1.3.5",
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
        'aioresponses~=0.7.2',
        'pyOpenSSL',
        'rsa',
        'requests',
        'python-jose~=3.2.0',
        'python-json-logger~=0.1.11',
        'beautifulsoup4~=4.8.0',
        'Jinja2~=2.11.3',
        'requests_pkcs12~=1.9',
        'requests-toolbelt~=0.9.1',
        'requests-mock~=1.7.0',
        'yattag~=1.12.2',
        'defusedxml~=0.7.1',
        'urllib3~=1.26.5',
        'py~=1.10.0'
    ],
    tests_require=['pytest'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
