# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Commandline tool to upload converted medra xml files to datacite."""

import json
import sys

import click
from lxml import etree

from .visitor import MedraVisitor


def write_to_file(nodes, output_dir, output_filename):
    """Write json to file."""


@click.group()
def cli():
    """Medra to datacite commandline tool."""
    pass


@cli.command()
@click.option("--input-file", required=True, type=click.File(mode="r"))
@click.option("--output-file", required=True, type=click.File(mode="w"))
@click.option(
    "--process-type",
    type=click.Choice(["article", "issue"], case_sensitive=False),
    default="article",
)
def transform(input_file, output_file, process_type):
    """Transform the combined xml file to single json files."""
    tree = etree.parse(input_file)
    visitor = MedraVisitor.create(process_type)

    try:
        visitor.visit(tree.getroot())
    except ValueError as e:
        print(e)
        sys.exit()

    json.dump(visitor.nodes, output_file)


if __name__ == "__main__":
    cli()
