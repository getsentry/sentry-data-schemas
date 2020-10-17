import os
import setuptools
import shutil

# Copies the schema in the module so that setuptools is able to
# find the file and add it to the package.
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
    install_requires=[
        "jsonschema-typed-v2==0.8.0"
    ],
    python_requires='>=3.8',
)