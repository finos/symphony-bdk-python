import setuptools


def readme():
    with open('README.md') as f:
        return f.read()


setuptools.setup(
    name="sym_api_client_python",
    version="0.1.14",
    author="Symphony Platform Solutions",
    author_email="platformsolutions@symphony.com",
    description="Symphony REST API - Python Client",
    long_description=readme(),
    long_description_content_type='text/markdown',
    url="https://github.com/SymphonyPlatformSolutions/"
        "symphony-api-client-python",
    packages=setuptools.find_packages(),
    install_requires=[
        'pyOpenSSL',
        'rsa',
        'requests',
        'python-jose',
        'urllib3',
    ],
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
