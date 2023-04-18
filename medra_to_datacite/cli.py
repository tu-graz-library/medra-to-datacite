# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Commandline tool to upload converted medra xml files to datacite."""

import json
import sys
from xml.etree.ElementTree import parse

from click import STRING, Choice, File, group, option, secho

from .visitor import MedraVisitorFactory


@group()
def cli():
    """Medra to datacite commandline tool."""
    pass


@cli.command()
@option("--input-file", required=True, type=File(mode="r"))
@option("--output-file", required=True, type=File(mode="w", encoding="utf-8"))
@option(
    "--process-type",
    type=Choice(["article", "issue"], case_sensitive=False),
    default="article",
)
@option("--namespace", required=True, type=STRING)
def transform(input_file, output_file, process_type, namespace):
    """Transform the combined xml file to single json files."""
    tree = parse(input_file)
    visitor = MedraVisitorFactory.create(process_type, namespace)

    try:
        visitor.visit(tree.getroot())
    except ValueError as e:
        secho(str(e), fg="red")
        sys.exit()

    json.dump(visitor.nodes, output_file, ensure_ascii=False)


if __name__ == "__main__":
    cli()
