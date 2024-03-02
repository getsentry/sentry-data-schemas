import json
import shutil
from typing import TYPE_CHECKING

import setuptools
from setuptools.command.sdist import sdist as _sdist

if TYPE_CHECKING:
    from openapi_pydantic import OpenAPI, Reference, Schema
    from typing import Iterator, Optional, Union, Generator

def convert_json_schema_to_openapi_schema(d: dict) -> dict:
    if '$ref' in d:
        return d

    if 'definitions' in d:
        for k, v in d['definitions'].items():
            d['definitions'][k] = convert_json_schema_to_openapi_schema(v)


    if 'anyOf' in d:
        if len(d['anyOf']) == 1:
            d.update(convert_json_schema_to_openapi_schema(d['anyOf'][0]))
            del d['anyOf']
        else:
            d['anyOf'] = [convert_json_schema_to_openapi_schema(v) for v in d['anyOf']]

    if 'type' in d:
        if isinstance(d['type'], list):
            if 'null' in d['type']:
                d['type'].remove('null')
                d['nullable'] = True

            if len(d['type']) == 1:
                d['type'] = d['type'][0]

    if 'items' in d:
        if isinstance(d['items'], list):
            d['prefixItems'] = [convert_json_schema_to_openapi_schema(v) for v in d['items']]
            del d['items']
        else:
            d['items'] = convert_json_schema_to_openapi_schema(d['items'])

    if 'properties' in d:
        for k, v in d['properties'].items():
            d['properties'][k] = convert_json_schema_to_openapi_schema(v)

    return d

class TypedDictsGenerator:
    spec: "OpenAPI | Schema"
    imports: set[str]
    lines: list[str]

    def __init__(self, spec: "OpenAPI"):
        self.spec = spec
        self.imports = set()
        self.lines = []

    def typing(self, t: str) -> str:
        self.imports.add("typing")
        return f"typing.{t}"

    def generate(self) -> list[str]:
        from openapi_pydantic import Schema, OpenAPI

        if isinstance(self.spec, OpenAPI):
            if self.spec.components and self.spec.components.schemas:
                for schema_ref, schema in self.spec.components.schemas.items():
                    self.lines.extend([*self.generate_schema(schema_ref, schema)])
                    self.lines.append("")
        else:
            self.lines.extend([*self.generate_schema(self.spec.title, self.spec)])
            self.lines.append("")

            for k, v in  self.spec.__pydantic_extra__.get('definitions', {}).items():
                self.lines.extend([*self.generate_schema(k, Schema.model_validate(v))])
                self.lines.append("")

        return [*(f"import {module}" for module in self.imports), "\n", *self.lines]

    def generate_schema(self, schema_ref: str, schema: "Schema") -> "Iterator[str]":
        if schema.description:
            yield from ["# " + v for v in schema.description.splitlines()]
        if schema.properties is not None:
            yield f"{schema_ref} = {self.typing('TypedDict')}({repr(schema_ref)}, {{"
            for prop_name, prop in schema.properties.items():
                annotation = yield from self.get_annotation(prop)
                yield f"    {repr(prop_name)}: {annotation},"
            yield "})"
        else:
            annotation = yield from self.get_annotation(schema)
            yield f"{schema_ref} = {annotation}"

    def get_annotation(
            self, schema: "Optional[Union[Reference, Schema, bool]]"
    ) -> "Generator[str, None, str]":
        from openapi_pydantic import Reference, Schema
        if isinstance(schema, Schema):
            if schema.default is not None:
                yield f"    # default: {repr(schema.default)}"
                inner_type = yield from self.get_annotation(schema.model_copy(update=dict(default=None)))
                return self.typing("NotRequired") + f"[{inner_type}]"

            if schema.schema_format:
                yield f"    # format: {schema.schema_format}"

            if schema.const:
                return self.typing(f"Literal[{repr(schema.const)}]")

            if schema.anyOf:
                parts = []
                for part in schema.anyOf:
                    annotation = yield from self.get_annotation(part)
                    parts.append(annotation)
                return f"{self.typing('Union')}[{', '.join(parts)}]"
            if schema.type == "object":
                annotation = yield from self.get_annotation(schema.additionalProperties)
                return self.typing(f"Mapping[str, {annotation}]")
            elif schema.type == "array":
                if (
                        schema.prefixItems
                        and schema.minItems == schema.maxItems
                        and schema.minItems == len(schema.prefixItems)
                ):
                    annotations = []
                    for prefix in schema.prefixItems:
                        annotation = yield from self.get_annotation(prefix)
                        annotations.append(annotation)
                    return self.typing(f"Tuple[{', '.join(annotations)}]")

                items = yield from self.get_annotation(schema.items)
                return self.typing(f"List[{items}]")
            elif schema.type == "string":
                return "str"
            elif schema.type == "null":
                return "None"
            elif schema.type == "number":
                return "float"
            elif schema.type == "integer":
                return "int"
            elif schema.type == "boolean":
                return "bool"
        elif isinstance(schema, Reference):
            return repr(schema.ref.split("/")[-1])
        return self.typing("Any")
class sdist(_sdist):
    schema_json_files = {"../relay/event.schema.json"}

    schema_jsons_to_type_files = {
        "../relay/event.schema.json": "sentry_data_schemas/events.py",
        "../seer/seer_api.json": "sentry_data_schemas/seer.py",
    }

    schema_jsons_to_distributed_json = {
        "../relay/event.schema.json": "sentry_data_schemas/event.schema.json",
        "../seer/seer_api.json": "sentry_data_schemas/seer_api.json",
    }

    def make_distribution(self):
        """
        Copy each individual project's schemas into the package
        """
        for src, dst in self.schema_jsons_to_distributed_json.items():
            shutil.copyfile(src, dst)

        from openapi_pydantic import OpenAPI, Schema
        for src, dst in self.schema_jsons_to_type_files.items():
            with open(src, "r") as source_schema, open(dst, "w") as output_types:
                if src in self.schema_json_files:
                    d = json.load(source_schema)
                    d = convert_json_schema_to_openapi_schema(d)
                    s = Schema.model_validate(d)
                else:
                    s = OpenAPI.model_validate(json.load(source_schema))
                output_types.write("\n".join(TypedDictsGenerator(s).generate()))

            from mypy import api
            so, se, status = api.run([dst])
            if status != 0:
                raise Exception(se)


        shutil.copyfile('../LICENSE', './LICENSE')
        with open("MANIFEST.in", "w") as manifest, open("MANIFEST.in.head", "r") as manifest_head:
            manifest.write(manifest_head.read())
            manifest.write("\n")
            manifest.writelines([
                f"include {schema_path}\n"
                for schema_path in self.schema_jsons_to_distributed_json.values()
            ])

        super().make_distribution()


def get_requirements(filename='requirements.txt'):
    with open(filename) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#") and x.strip()]


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sentry-data-schemas",
    version=open("VERSION").read().strip(),
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
    setup_requires=get_requirements("setup-requirements.txt"),
    python_requires='>=3.11',  # For strongest typing behaviors.
    classifiers={
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development",
        "License :: MIT",
    },
    cmdclass={
        'sdist': sdist
    },
)
