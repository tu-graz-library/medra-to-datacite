#!/usr/bin/env sh
# -*- coding: utf-8 -*-
#
# Copyright (C) 2020-2023 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


ruff .
python -m pytest
