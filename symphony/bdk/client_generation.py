#!/usr/bin/env python
import sys
import os
from collections import OrderedDict
import requests
import subprocess

API_BASE_URL = "https://raw.githubusercontent.com/symphonyoss/symphony-api-spec/20.9"
APIS_TO_GENERATE = OrderedDict(
    [
        ("Agent", "agent/agent-api-public.yaml"),
        ("Pod", "pod/pod-api-public-deprecated.yaml"),
        ("Auth", "authenticator/authenticator-api-public.yaml"),
        ("Login", "login/login-api-public.yaml"),
    ]
)
BUILD_DIR = os.path.dirname(os.path.realpath(__file__))  # Where we run the script
GENERATOR_FOLDER = BUILD_DIR + "/openapitools"
GENERATOR_NAME = "/openapi-generator-cli.sh"
GENERATOR_TYPE = "python"
GENERATOR_SCRIPT = GENERATOR_FOLDER + GENERATOR_NAME
GENERATED_FOLDER = BUILD_DIR + "/generated/openapi"

# TODO: Add logging
def download_task(api, path):
    print("DOWNLOADING ", path, "...")
    specfile_url = API_BASE_URL + "/" + path
    r = requests.get(specfile_url)
    # TODO handle exceptions and errors of get request (spike for all requests, I think we can automate handling of exceptions)
    specfile = open(
        BUILD_DIR + "/" + path.split("/")[1], "wb"
    )  # TODO: Add url formatter or better write this shit
    specfile.write(r.content)
    specfile.close()


def install_generator():
    if os.path.exists(GENERATOR_SCRIPT) == False:
        try:
            os.mkdir(GENERATOR_FOLDER)
        except OSError:
            print("Creation of the directory %s failed" % GENERATOR_FOLDER)
        else:
            print("Successfully created the directory %s " % GENERATOR_FOLDER)
            r = requests.get(
                "https://raw.githubusercontent.com/OpenAPITools/openapi-generator/master/bin/utils/openapi-generator-cli.sh"
            )

            openapi_cli = open(
                GENERATOR_FOLDER + GENERATOR_NAME, "wb"
            )  # TODO: Add url formatter or better write this shit
            openapi_cli.write(r.content)
            openapi_cli.close()
            print("Successfully downloaded the generator")
    else:
        print("Generator exists.")


def generate(download_specs=True):
    # Run the launcher script
    # install_generator()
    # os.system("chmod u+x " + GENERATOR_FOLDER + GENERATOR_NAME)
    # subprocess.run([GENERATOR_FOLDER + GENERATOR_NAME, "version"])

    for api, path in APIS_TO_GENERATE.items():
        if download_specs:
            download_task(api, path)
            print("Completed Download task for", api)
        print("starting code generation ... ")
        generate_command = "generate -i {} -g {} -o {}".format(
            BUILD_DIR + "/" + path.split("/")[1], GENERATOR_TYPE, GENERATED_FOLDER
        )
        # run the launcher script
        # subprocess.run([GENERATOR_FOLDER + GENERATOR_NAME, *generate_command.split(" ")])

        # Run the pip library
        subprocess.run(["openapi-generator", *generate_command.split(" ")])
        print("Completed code generation for", api)


if __name__ == "__main__":
    generate()