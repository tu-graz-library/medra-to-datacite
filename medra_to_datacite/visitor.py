# -*- coding: utf-8 -*-
#
# Copyright (C) 2020 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
MedraVisitor.

This visitor transforms a xml file represenation of the medra standard into
json file representation of the datacite standard.
"""


from typing import List

from lxml import etree

from .helper import debug, xsd_ns


class MedraVisitor:
    """MedraVisitor class."""

    nodes: List[dict] = []
    node: dict = {
        "metadata": {},
        "doi": "",
        "id": "",
        "url": "",
    }
    titles: List[dict] = []

    def __init__(self, test_mode=True, prefix=None, test_prefix=None):
        if test_mode and (prefix is None or test_prefix is None):
            raise ValueError(
                "if the test_mode is activate the prefix and the test_prefix has to be set"
            )

        self.test_mode = test_mode
        self.prefix = prefix
        self.test_prefix = test_prefix

    @debug
    def create(process_type, test_mode=True, prefix=None, test_prefix=None):
        """Create the medra visitor."""
        if process_type == "article":
            return DOISerialArticleWork(test_mode, prefix, test_prefix)
        elif process_type == "issue":
            return DOISerialIssueWork(test_mode, prefix, test_prefix)
        else:
            raise ValueError("wrong schema given")

    @debug
    def process(self, node, parent):
        """Execute the corresponding method to the tag name."""

        def func_not_found(*args, **kwargs):
            localname = etree.QName(node).localname
            namespace = etree.QName(node).namespace
            raise ValueError(f"NO visitor node: '{localname}' ns: '{namespace}'")

        tag_name = etree.QName(node).localname
        visit_func = getattr(self, f"visit_{tag_name}", func_not_found)
        result = visit_func(node, parent)
        return result

    @debug
    def extend(self, key, value):
        if key not in self.node["metadata"]:
            self.node["metadata"][key] = []

        self.node["metadata"][key].extend(value)

    @debug
    def init_node(self):
        self.node = {
            "metadata": {},
            "doi": "",
            "id": "",
            "url": "",
        }

    @debug
    def visit(self, node, parent=None):
        """Visit default method and entry point for the class."""
        for child in node:
            self.process(child, parent=node)

    @debug
    def visit_Header(self, node, parent):
        """Visit method for Header tag."""
        pass

    @debug
    def visit_NotificationType(self, node, parent=None):
        """Visit method for NotificationType tag."""
        pass

    @debug
    def visit_DOI(self, node, parent=None):
        """Visit method for DOI tag."""
        doi = node.text

        if self.test_mode:
            doi = doi.replace(self.prefix, self.test_prefix)

        self.node["doi"] = doi
        pass

    @debug
    def visit_DOIWebsiteLink(self, node, parent=None):
        """Visit method for DOIWebsiteLink tag."""
        self.node["url"] = node.text
        pass

    @debug
    def visit_DOIStructuralType(self, node, parent=None):
        """Visit method for DOIStructuralType tag."""
        pass

    @debug
    def visit_RegistrantName(self, node, parent=None):
        """Visit method for RegistrantName tag."""
        self.node["metadata"]["publisher"] = node.text

    @debug
    def visit_RegistrationAuthority(self, node, parent=None):
        """Visit method for RegistrationAuthority tag."""
        pass

    @debug
    def visit_WorkIdentifier(self, node, parent=None):
        """Visit method for WorkIdentifier tag."""
        pass

    @debug
    def visit_SerialPublication(self, node, parent=None):
        """Visit method for SerialPublication tag."""
        self.visit(node, parent)

    @debug
    def visit_SerialWork(self, node, parent=None):
        """Visit method for SerialWork tag."""
        pass

    @debug
    def visit_SerialVersion(self, node, parent=None):
        """Visit method for SerialVersion tag."""
        pass

    @debug
    def visit_Title(self, node, parent=None):
        """Visit method for Title tag."""
        self.titles.append(
            {
                "title": node.find(xsd_ns("TitleText")).text,
                "lang": node.xpath("string(@language)"),
            }
        )

    @debug
    def visit_Publisher(self, node, parent=None):
        """Visit method for Publisher tag."""
        publisher = node.find(xsd_ns("PublisherName")).text
        self.node["metadata"]["publisher"] += f" & {publisher}"
        pass

    @debug
    def visit_CountryOfPublication(self, node, parent=None):
        """Visit method for CountryOfPublication tag."""
        pass

    @debug
    def visit_JournalIssue(self, node, parent=None):
        """Visit method for JournalIssue tag."""
        pass

    @debug
    def visit_JournalVolumeNumber(self, node, parent=None):
        """Visit method for JournalVolumeNumber tag."""
        pass

    @debug
    def visit_JournalIssueNumber(self, node, parent=None):
        """Visit method for JournalIssueNumber tag."""
        pass

    @debug
    def visit_JournalIssueDesignation(self, node, parent=None):
        """Visit method for JournalIsseDesignation tag."""
        pass

    @debug
    def visit_JournalIssueDate(self, node, parent=None):
        """Visit method for JournalIssueDate tag."""
        pass

    @debug
    def visit_ContentItem(self, node, parent=None):
        """Visit method for ContentItem tag."""
        self.titles = []
        self.abstracts = []
        self.node["metadata"]["creators"] = []

        self.visit(node, parent)

        self.node["metadata"]["titles"] = self.titles
        self.extend("descriptions", self.abstracts)

    @debug
    def visit_SequenceNumber(self, node, parent=None):
        """Visit method for SequenceNumber tag."""
        pass

    @debug
    def visit_TextItem(self, node, parent=None):
        """Visit method for TextItem tag."""
        pass

    @debug
    def visit_Contributor(self, node, parent=None):
        """Visit method for Contributor tag."""
        self.contributor = {}
        self.affiliations = []
        self.visit(node, parent)

        if len(self.affiliations) > 0:
            self.contributor["affiliation"] = self.affiliations

        # NOTE: there seams not to be a creators in medra
        self.node["metadata"]["creators"].append(self.contributor)

    @debug
    def visit_ContributorRole(self, node, parent=None):
        """Visit method for ContributorRole tag."""
        pass

    @debug
    def visit_PersonName(self, node, parent=None):
        """Visit method for PersonName tag."""
        pass

    @debug
    def visit_PersonNameInverted(self, node, parent=None):
        """Visit method for PersonNameInverted tag."""
        self.contributor["name"] = node.text
        self.contributor["nameType"] = "Personal"
        pass

    @debug
    def visit_KeyNames(self, node, parent=None):
        """Visit method for KeyNames tag."""
        pass

    @debug
    def visit_ProfessionalAffiliation(self, node, parent=None):
        """Visit method for ProfessionalAffiliation tag."""
        self.affiliations.append({"name": node.find(xsd_ns("Affiliation")).text})
        pass

    @debug
    def visit_Language(self, node, parent=None):
        """Visit method for Language tag."""
        pass

    @debug
    def visit_OtherText(self, node, parent=None):
        """Visit method for OtherText tag."""
        self.abstracts.append(
            {
                "description": node.find(xsd_ns("Text")).text.strip(),
                "descriptionType": "Abstract",
            }
        )
        pass

    @debug
    def visit_PublicationDate(self, node, parent=None):
        """Visit method for PublicationDate tag."""
        self.node["metadata"]["publicationYear"] = node.text[:4]

    @debug
    def visit_RelatedWork(self, node, parent=None):
        """Visit method for RelatedWork tag."""
        pass

    @debug
    def visit_RelationCode(self, node, parent=None):
        """Visit method for RelationCode tag."""
        pass

    @debug
    def visit_RelatedProduct(self, node, parent=None):
        """Visit method for RelatedProduct tag."""
        pass

    @debug
    def visit_BiographicalNote(self, node, parent=None):
        """Visit method for BiographicalNote tag."""
        pass


class DOISerialArticleWork(MedraVisitor):
    """DOISerialArticleWork class."""

    @debug
    def visit_DOISerialArticleWork(self, node, parent):
        """Visit method for DOISerialArticleWork tag."""
        self.init_node()

        self.visit(node, parent)

        self.node["id"] = f"https://doi.org/{self.node['doi']}"
        self.node["metadata"]["types"] = {
            "resourceTypeGeneral": "DataPaper",
            "resourceType": "Article",
        }
        self.node["metadata"]["schemaVersion"] = "http://datacite.org/schema/kernel-4"
        self.node["metadata"]["identifiers"] = [
            {"identifierType": "DOI", "identifier": self.node["doi"]}
        ]

        self.nodes.append(self.node)

    @debug
    def visit_SerialWork(self, node, parent=None):
        """Visit method for SerialWork tag."""
        self.titles = []
        self.visit(node, parent)

        descriptions = [
            {"description": obj["title"], "descriptionType": "SeriesInformation"}
            for obj in self.titles
        ]

        self.extend("descriptions", descriptions)


class DOISerialIssueWork(MedraVisitor):
    @debug
    def init_node(self):
        super().init_node()
        self.node["metadata"] = {"creators": [{"name": ":none"}]}

    @debug
    def visit_DOISerialIssueWork(self, node, parent):
        self.init_node()
        self.abstracts = []

        self.visit(node, parent)

        if len(self.abstracts) > 0:
            self.extend("descriptions", self.abstracts)

        self.node["id"] = f"https://doi.org/{self.node['doi']}"
        self.node["metadata"]["types"] = {
            "resourceTypeGeneral": "Collection",
            "resourceType": "Issue",
        }
        self.node["metadata"]["schemaVersion"] = "http://datacite.org/schema/kernel-4"
        self.node["metadata"]["identifiers"] = [
            {"identifierType": "DOI", "identifier": self.node["doi"]}
        ]

        self.nodes.append(self.node)

    @debug
    def visit_WorkIdentifier(self, node, parent=None):
        """Visit method for WorkIdentifier tag."""

        if node.find(xsd_ns("WorkIDType")).text != "06":
            return

        self.extend(
            "relatedIdentifiers",
            [
                {
                    "relatedIdentifier": node.find(xsd_ns("IDValue")).text,
                    "relatedIdentifierType": "DOI",
                    "relationType": "IsSupplementedBy",
                }
            ],
        )

    @debug
    def visit_SerialWork(self, node, parent=None):
        """Visit method for SerialWork tag."""
        self.titles = []

        self.visit(node, parent)

        self.node["metadata"]["titles"] = self.titles

    @debug
    def visit_JournalIssue(self, node, parent=None):
        """Visit method for JournalIssue tag."""
        self.visit(node, parent=parent)

    @debug
    def visit_JournalIssueDesignation(self, node, parent=None):
        """Visit method for JournalIsseDesignation tag."""
        self.extend(
            "descriptions",
            [{"description": node.text, "descriptionType": "SeriesInformation"}],
        )

    @debug
    def visit_RelatedWork(self, node, parent=None):
        """Visit method for RelatedWork tag."""
        self.visit(node, parent=parent)
