import os
import setuptools
import shutil

def get_requirements():
    with open(u"requirements.txt") as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]
    

# Copies the schema in the module so that setuptools is able to
# find the file and add it to the package.
#
# We need to check if the file is present before running the copy
# because, depending where the package is imported from the file
# may or may not be there.
# When producing the distribution, the file is copied into the 
# distribution.
# When importing from a distribution the copy must be skipped since
# the file is already in the right place and the source is not
# available.
#
# TODO: Try to perform this copy only when building the distribution
# by extending the sdist command.
if os.path.isfile("../relay/event.schema.json"):
    shutil.copyfile(
        "../relay/event.schema.json",
        "./sentry_data_schemas/event.schema.json"
    )
if os.path.isfile("../LICENSE"):
    shutil.copyfile(
        "../LICENSE",
        "./LICENSE"
    )

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentry-data-schemas",
    version="0.0.1",
    author="Sentry",
    license="MIT",
    author_email="oss@sentry.io",
    description="Sentry shared data schemas",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/getsentry/sentry-data-schemas",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=get_requirements(),
    python_requires='>=3.7', # The minimum required by jsonschema-typed
    classifiers={
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "License :: MIT",
    }
)
