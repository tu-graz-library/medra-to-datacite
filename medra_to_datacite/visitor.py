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

import typecheck as tc
from lxml import etree
from lxml.etree import _Element as Element

from .helper import xsd_ns


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

    def create(process_type, test_mode=True, prefix=None, test_prefix=None):
        """Create the medra visitor."""
        if process_type == "article":
            return DOISerialArticleWork(test_mode, prefix, test_prefix)
        elif process_type == "issue":
            return DOISerialIssueWork(test_mode, prefix, test_prefix)
        else:
            raise ValueError("wrong schema given")

    @tc.typecheck
    def process(self, node: Element):
        """Execute the corresponding method to the tag name."""

        def func_not_found(*args, **kwargs):
            localname = etree.QName(node).localname
            namespace = etree.QName(node).namespace
            raise ValueError(f"NO visitor node: '{localname}' ns: '{namespace}'")

        tag_name = etree.QName(node).localname
        visit_func = getattr(self, f"visit_{tag_name}", func_not_found)
        result = visit_func(node)
        return result

    @tc.typecheck
    def append(self, key: str, value: dict):
        if key not in self.node["metadata"]:
            self.node["metadata"][key] = []

        if value not in self.node["metadata"][key]:
            self.node["metadata"][key].append(value)

    @tc.typecheck
    def init_node(self):
        self.node = {
            "metadata": {},
            "doi": "",
            "id": "",
            "url": "",
        }

    @tc.typecheck
    def visit(self, node: Element):
        """Visit default method and entry point for the class."""
        for child in node:
            self.process(child)

    @tc.typecheck
    def visit_Header(self, node: Element):
        """Visit method for Header tag."""
        pass

    @tc.typecheck
    def visit_NotificationType(self, node: Element):
        """Visit method for NotificationType tag."""
        pass

    @tc.typecheck
    def visit_DOI(self, node: Element):
        """Visit method for DOI tag."""
        doi = node.text

        if self.test_mode:
            doi = doi.replace(self.prefix, self.test_prefix)

        self.node["doi"] = doi

    @tc.typecheck
    def visit_DOIWebsiteLink(self, node: Element):
        """Visit method for DOIWebsiteLink tag."""
        self.node["url"] = node.text

    @tc.typecheck
    def visit_DOIStructuralType(self, node: Element):
        """Visit method for DOIStructuralType tag."""
        pass

    @tc.typecheck
    def visit_RegistrantName(self, node: Element):
        """Visit method for RegistrantName tag."""
        self.node["metadata"]["publisher"] = node.text

    @tc.typecheck
    def visit_RegistrationAuthority(self, node: Element):
        """Visit method for RegistrationAuthority tag."""
        pass

    @tc.typecheck
    def visit_WorkIdentifier(self, node: Element):
        """Visit method for WorkIdentifier tag."""
        pass

    @tc.typecheck
    def visit_SerialPublication(self, node: Element):
        """Visit method for SerialPublication tag."""
        self.visit(node)

    @tc.typecheck
    def visit_SerialWork(self, node: Element):
        """Visit method for SerialWork tag."""
        pass

    @tc.typecheck
    def visit_SerialVersion(self, node: Element):
        """Visit method for SerialVersion tag."""
        pass

    @tc.typecheck
    def visit_Title(self, node: Element):
        """Visit method for Title tag."""
        self.titles.append(
            {
                "title": node.find(xsd_ns("TitleText")).text,
                "lang": node.xpath("string(@language)"),
            }
        )

    @tc.typecheck
    def visit_Publisher(self, node: Element):
        """Visit method for Publisher tag."""
        publisher = node.find(xsd_ns("PublisherName")).text
        self.node["metadata"]["publisher"] += f" & {publisher}"

    @tc.typecheck
    def visit_CountryOfPublication(self, node: Element):
        """Visit method for CountryOfPublication tag."""
        pass

    @tc.typecheck
    def visit_JournalIssue(self, node: Element):
        """Visit method for JournalIssue tag."""
        pass

    @tc.typecheck
    def visit_JournalVolumeNumber(self, node: Element):
        """Visit method for JournalVolumeNumber tag."""
        pass

    @tc.typecheck
    def visit_JournalIssueNumber(self, node: Element):
        """Visit method for JournalIssueNumber tag."""
        pass

    @tc.typecheck
    def visit_JournalIssueDesignation(self, node: Element):
        """Visit method for JournalIsseDesignation tag."""
        pass

    @tc.typecheck
    def visit_JournalIssueDate(self, node: Element):
        """Visit method for JournalIssueDate tag."""
        pass

    @tc.typecheck
    def visit_ContentItem(self, node: Element):
        """Visit method for ContentItem tag."""
        self.titles = []
        self.abstracts = []
        self.node["metadata"]["creators"] = []

        self.visit(node)

        self.node["metadata"]["titles"] = self.titles

        for abstract in self.abstracts:
            self.append("descriptions", abstract)

    @tc.typecheck
    def visit_SequenceNumber(self, node: Element):
        """Visit method for SequenceNumber tag."""
        pass

    @tc.typecheck
    def visit_TextItem(self, node: Element):
        """Visit method for TextItem tag."""
        pass

    @tc.typecheck
    def visit_Contributor(self, node: Element):
        """Visit method for Contributor tag."""
        self.contributor = {}
        self.affiliations = []
        self.visit(node)

        if len(self.affiliations) > 0:
            self.contributor["affiliation"] = self.affiliations

        # NOTE: there seams not to be a creators in medra
        self.node["metadata"]["creators"].append(self.contributor)

    @tc.typecheck
    def visit_ContributorRole(self, node: Element):
        """Visit method for ContributorRole tag."""
        pass

    @tc.typecheck
    def visit_PersonName(self, node: Element):
        """Visit method for PersonName tag."""
        pass

    @tc.typecheck
    def visit_PersonNameInverted(self, node: Element):
        """Visit method for PersonNameInverted tag."""
        self.contributor["name"] = node.text
        self.contributor["nameType"] = "Personal"

    @tc.typecheck
    def visit_KeyNames(self, node: Element):
        """Visit method for KeyNames tag."""
        pass

    @tc.typecheck
    def visit_NamesBeforeKey(self, node: Element):
        """Visit method for NamesBeforeKey tag."""
        pass

    @tc.typecheck
    def visit_ProfessionalAffiliation(self, node: Element):
        """Visit method for ProfessionalAffiliation tag."""
        self.affiliations.append({"name": node.find(xsd_ns("Affiliation")).text})

    @tc.typecheck
    def visit_Language(self, node: Element):
        """Visit method for Language tag."""
        pass

    @tc.typecheck
    def visit_OtherText(self, node: Element):
        """Visit method for OtherText tag."""
        self.abstracts.append(
            {
                "description": node.find(xsd_ns("Text")).text.strip(),
                "descriptionType": "Abstract",
            }
        )

    @tc.typecheck
    def visit_PublicationDate(self, node: Element):
        """Visit method for PublicationDate tag."""
        self.node["metadata"]["publicationYear"] = node.text[:4]

    @tc.typecheck
    def visit_RelatedWork(self, node: Element):
        """Visit method for RelatedWork tag."""
        pass

    @tc.typecheck
    def visit_RelationCode(self, node: Element):
        """Visit method for RelationCode tag."""
        pass

    @tc.typecheck
    def visit_RelatedProduct(self, node: Element):
        """Visit method for RelatedProduct tag."""
        pass

    @tc.typecheck
    def visit_BiographicalNote(self, node: Element):
        """Visit method for BiographicalNote tag."""
        pass


class DOISerialArticleWork(MedraVisitor):
    """DOISerialArticleWork class."""

    @tc.typecheck
    def visit_DOISerialArticleWork(self, node: Element):
        """Visit method for DOISerialArticleWork tag."""
        self.init_node()

        self.visit(node)

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

    @tc.typecheck
    def visit_SerialWork(self, node: Element):
        """Visit method for SerialWork tag."""
        self.titles = []
        self.visit(node)

        for obj in self.titles:
            description = {
                "description": obj["title"],
                "descriptionType": "SeriesInformation",
            }
            self.append("descriptions", description)


class DOISerialIssueWork(MedraVisitor):
    @tc.typecheck
    def init_node(self):
        super().init_node()
        self.node["metadata"] = {"creators": [{"name": ":none"}]}

    @tc.typecheck
    def visit_DOISerialIssueWork(self, node: Element):
        self.init_node()
        self.abstracts = []

        self.visit(node)

        for abstract in self.abstracts:
            self.append("descriptions", abstract)

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

    @tc.typecheck
    def visit_WorkIdentifier(self, node: Element):
        """Visit method for WorkIdentifier tag."""

        if node.find(xsd_ns("WorkIDType")).text != "06":
            return

        self.append(
            "relatedIdentifiers",
            {
                "relatedIdentifier": node.find(xsd_ns("IDValue")).text,
                "relatedIdentifierType": "DOI",
                "relationType": "IsSupplementedBy",
            },
        )

    @tc.typecheck
    def visit_SerialWork(self, node: Element):
        """Visit method for SerialWork tag."""
        self.titles = []

        self.visit(node)

        self.node["metadata"]["titles"] = self.titles

    @tc.typecheck
    def visit_JournalIssue(self, node: Element):
        """Visit method for JournalIssue tag."""
        self.visit(node)

    @tc.typecheck
    def visit_JournalIssueDesignation(self, node: Element):
        """Visit method for JournalIsseDesignation tag."""
        self.append(
            "descriptions",
            {"description": node.text, "descriptionType": "SeriesInformation"},
        )

    @tc.typecheck
    def visit_RelatedWork(self, node: Element):
        """Visit method for RelatedWork tag."""
        self.visit(node)
