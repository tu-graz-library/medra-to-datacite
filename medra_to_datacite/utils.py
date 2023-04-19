#########################################################
#
# Copyright (C) 2020-2023 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""Utils."""

from xml.etree.ElementTree import Element


class QName:
    """Local Rewrite for lxml.etree.QName."""

    def __init__(self, node: Element) -> None:
        """Construct QName."""
        self.node = node

    @property
    def localname(self) -> str:
        """Return localname from node with xpath."""
        return self.node.tag.split("}")[-1]

    @property
    def namespace(self) -> str:
        """Return namespace from node with xpath."""
        return self.node.tag.split("}")[0][1:]
