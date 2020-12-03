#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

pydocstyle **/*.py
mypy --color-output --no-error-summary --ignore-missing-imports **/*.py
flake8 **/*.py
isort **/*.py --quiet --check-only --diff
check-manifest --quiet --ignore ".travis-*" --ignore ".*-requirements.txt"
sphinx-build -qnNW docs docs/_build/html

# python -m pydocstyle medra_to_datacite tests docs
# python -m isort medra_to_datacite --check-only --diff
# python -m check_manifest
# python -m sphinx.cmd.build -qnNW docs docs/_build/html


