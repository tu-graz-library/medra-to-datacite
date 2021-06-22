# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Commandline tool to upload converted medra xml files to datacite."""

import json
import os

import click
from datacite import DataCiteRESTClient, schema43
from datacite.errors import DataCiteError
from jsonschema import ValidationError
from lxml import etree

from .visitor import MedraVisitor


def valid(instance):
    """Validate the json object."""

    if schema43.validate(instance):
        return True

    try:
        schema43.validator.validate(instance)
    except ValidationError as e:
        print(e.args[0])

    return False


def get_config():
    """Get the configuration variables from the environment."""

    username = os.getenv("DATACITE_API_USERNAME")
    password = os.getenv("DATACITE_API_PASSWORD")
    prefix = os.getenv("DATACITE_PREFIX")
    test_prefix = os.getenv("DATACITE_TEST_PREFIX")

    return (username, password, prefix, test_prefix)


def rebuildAsDataciteUploadJson(node, prefix):
    """Uploaded file differes a little bit from the structure."""
    data = {}
    data["attributes"] = node["metadata"]
    data["attributes"]["prefix"] = prefix
    data["attributes"]["event"] = "publish"
    data["attributes"]["url"] = node["url"]
    data["attributes"]["doi"] = node["doi"]
    return {"data": data}


def saveErrorMetadata(metadata):
    """Write the metadata which is wrong to a predefined file."""
    with open("error.json", "w", encoding="utf-8") as fp:
        json.dump(metadata, fp, ensure_ascii=False, indent=4)


@click.group()
def cli():
    """Medra to datacite commandline tool."""
    pass


@cli.command()
@click.option("--input-file", required=True, type=click.File(mode="r"))
@click.option("--output-dir", required=True, type=click.Path(exists=True))
@click.option("--test-mode/--production-mode", default=True, is_flag=True)
@click.option(
    "--process-type",
    type=click.Choice(["article", "issue"], case_sensitive=False),
    default="article",
)
def transform(input_file, output_dir, test_mode, process_type):
    """Transform the combined xml file to single json files."""
    prod_prefix, test_prefix = get_config()[2:]
    prefix = test_prefix if test_mode else prod_prefix

    tree = etree.parse(input_file)
    visitor = MedraVisitor.create(process_type, test_mode, prod_prefix, test_prefix)

    try:
        visitor.visit(tree.getroot())
    except ValueError as e:
        print(e)

    for node in visitor.nodes:
        if not valid(node["metadata"]):
            saveErrorMetadata(node["metadata"])
            print("There is at least one NOT valid transformation.")
            exit()

    for node in visitor.nodes:
        doi_as_filename = node["doi"].replace("/", "-").replace(".", "-")
        out_filename = f"{output_dir}/{doi_as_filename}.json"

        datacite_json = rebuildAsDataciteUploadJson(node, prefix)

        with open(out_filename, "w") as outfile:
            json.dump(datacite_json, outfile)


@cli.command()
@click.option("--input-file", required=True, type=click.File(mode="r"))
@click.option("--test-mode/--production-mode", default=True, is_flag=True)
@click.option(
    "--process-type",
    type=click.Choice(["article", "issue"], case_sensitive=False),
    default="article",
)
def upload(input_file, test_mode, process_type):
    """Upload converted medra xml files to datacite."""

    username, password, prod_prefix, test_prefix = get_config()

    prefix = test_prefix if test_mode else prod_prefix
    tree = etree.parse(input_file)
    visitor = MedraVisitor.create(process_type, test_mode, prod_prefix, test_prefix)

    d = DataCiteRESTClient(
        username=username,
        password=password,
        test_mode=test_mode,
        prefix=prefix,
    )

    try:
        visitor.visit(tree.getroot())
    except ValueError as e:
        print(e)

    for node in visitor.nodes:
        if not valid(node["metadata"]):
            print("There is at least one NOT valid transformation.")
            exit()

    try:
        for node in visitor.nodes:
            d.public_doi(node["metadata"], node["url"], node["doi"])

    except DataCiteError as e:
        print("DataCiteError")
        print(json.dumps(json.loads(str(e)), indent=4, sort_keys=True))


if __name__ == "__main__":
    cli()
