#########################################################
#
# Copyright (C) 2020-2023 Graz University of Technology
#
# medra-to-datacite is free software; you can redistribute it and/or modify
# it under the terms of the MIT License; see LICENSE file for more details.

"""
MedraVisitor.

This visitor transforms a xml file represenation of the medra standard into
json file representation of the datacite standard.
"""
from typing import Union
from xml.etree.ElementTree import Element

from .utils import QName


class MedraVisitorFactory:
    """Factory class for MedraVisitor."""

    @classmethod
    def create(
        cls,
        process_type: str,
        namespace: str,
    ) -> Union["DOISerialArticleWork", "DOISerialIssueWork"]:
        """Create the medra visitor."""
        if process_type == "article":
            return DOISerialArticleWork(namespace)

        if process_type == "issue":
            return DOISerialIssueWork(namespace)

        msg = "wrong schema given"
        raise ValueError(msg)


class MedraVisitor:
    """MedraVisitor class."""

    nodes: list[dict] = []
    node: dict = {
        "metadata": {},
        "doi": "",
        "url": "",
    }
    titles: list[dict] = []

    def __init__(self, namespace: str) -> None:
        """Construct MedraVisitor."""
        self.namespace = {"": namespace}

    def process(self, node: Element) -> None:
        """Execute the corresponding method to the tag name."""

        def func_not_found(*_: dict, **__: dict) -> None:
            localname = QName(node).localname
            namespace = QName(node).namespace
            msg = f"NO visitor node: '{localname}' ns: '{namespace}'"
            raise ValueError(msg)

        tag_name = QName(node).localname
        visit_func = getattr(self, f"visit_{tag_name}", func_not_found)
        return visit_func(node)

    def append(self, key: str, value: dict) -> None:
        """Append to corresponding key."""
        if key not in self.node["metadata"]:
            self.node["metadata"][key] = []

        if value not in self.node["metadata"][key]:
            self.node["metadata"][key].append(value)

    def init_node(self) -> None:
        """Init node."""
        self.node = {
            "metadata": {},
            "doi": "",
            "url": "",
        }

    def visit(self, node: Element) -> None:
        """Visit default method and entry point for the class."""
        for child in node:
            self.process(child)

    def visit_Header(self, node: Element) -> None:
        """Visit method for Header tag."""

    def visit_NotificationType(self, node: Element) -> None:
        """Visit method for NotificationType tag."""

    def visit_DOI(self, node: Element) -> None:
        """Visit method for DOI tag."""
        self.node["doi"] = node.text

    def visit_DOIWebsiteLink(self, node: Element) -> None:
        """Visit method for DOIWebsiteLink tag."""
        self.node["url"] = node.text

    def visit_DOIStructuralType(self, node: Element) -> None:
        """Visit method for DOIStructuralType tag."""

    def visit_RegistrantName(self, node: Element) -> None:
        """Visit method for RegistrantName tag."""
        self.node["metadata"]["publisher"] = node.text

    def visit_RegistrationAuthority(self, node: Element) -> None:
        """Visit method for RegistrationAuthority tag."""

    def visit_WorkIdentifier(self, node: Element) -> None:
        """Visit method for WorkIdentifier tag."""

    def visit_SerialPublication(self, node: Element) -> None:
        """Visit method for SerialPublication tag."""
        self.visit(node)

    def visit_SerialWork(self, node: Element) -> None:
        """Visit method for SerialWork tag."""

    def visit_SerialVersion(self, node: Element) -> None:
        """Visit method for SerialVersion tag."""

    def visit_Title(self, node: Element) -> None:
        """Visit method for Title tag."""
        self.titles.append(
            {
                "title": node.find("TitleText", self.namespace).text,
                "lang": node.get("language"),
            },
        )

    def visit_Publisher(self, node: Element) -> None:
        """Visit method for Publisher tag."""
        publisher = node.find("PublisherName", self.namespace).text
        self.node["metadata"]["publisher"] += f" & {publisher}"

    def visit_CountryOfPublication(self, node: Element) -> None:
        """Visit method for CountryOfPublication tag."""

    def visit_JournalIssue(self, node: Element) -> None:
        """Visit method for JournalIssue tag."""

    def visit_JournalVolumeNumber(self, node: Element) -> None:
        """Visit method for JournalVolumeNumber tag."""

    def visit_JournalIssueNumber(self, node: Element) -> None:
        """Visit method for JournalIssueNumber tag."""

    def visit_JournalIssueDesignation(self, node: Element) -> None:
        """Visit method for JournalIsseDesignation tag."""

    def visit_JournalIssueDate(self, node: Element) -> None:
        """Visit method for JournalIssueDate tag."""

    def visit_ContentItem(self, node: Element) -> None:
        """Visit method for ContentItem tag."""
        self.titles = []
        self.abstracts = []
        self.node["metadata"]["creators"] = []

        self.visit(node)

        self.node["metadata"]["titles"] = self.titles

        for abstract in self.abstracts:
            self.append("descriptions", abstract)

    def visit_SequenceNumber(self, node: Element) -> None:
        """Visit method for SequenceNumber tag."""

    def visit_TextItem(self, node: Element) -> None:
        """Visit method for TextItem tag."""

    def visit_Contributor(self, node: Element) -> None:
        """Visit method for Contributor tag."""
        self.contributor = {}
        self.affiliations = []
        self.visit(node)

        if len(self.affiliations) > 0:
            self.contributor["affiliation"] = self.affiliations

        # NOTE: there seams not to be a creators in medra
        self.node["metadata"]["creators"].append(self.contributor)

    def visit_ContributorRole(self, node: Element) -> None:
        """Visit method for ContributorRole tag."""

    def visit_NameIdentifier(self, node: Element) -> None:
        """Visit method for NameIdentifier tag."""
        name_id_type = node.find("NameIDType", self.namespace).text

        if name_id_type == "21":
            self.contributor["nameIdentifier"] = {
                "nameIdentifier": node.find("IDValue", self.namespace).text,
                "nameIdentifierScheme": "ORCID",
                "schemeURI": "https://orcid.org/",
            }
        else:
            msg = "type not yet implemented"
            raise ValueError(msg)

    def visit_PersonName(self, node: Element) -> None:
        """Visit method for PersonName tag."""

    def visit_PersonNameInverted(self, node: Element) -> None:
        """Visit method for PersonNameInverted tag."""
        self.contributor["name"] = node.text
        self.contributor["nameType"] = "Personal"

    def visit_KeyNames(self, node: Element) -> None:
        """Visit method for KeyNames tag."""

    def visit_NamesBeforeKey(self, node: Element) -> None:
        """Visit method for NamesBeforeKey tag."""

    def visit_ProfessionalAffiliation(self, node: Element) -> None:
        """Visit method for ProfessionalAffiliation tag."""
        self.affiliations.append(
            {"name": node.find("Affiliation", self.namespace).text},
        )

    def visit_Language(self, node: Element) -> None:
        """Visit method for Language tag."""

    def visit_OtherText(self, node: Element) -> None:
        """Visit method for OtherText tag."""
        self.abstracts.append(
            {
                "description": node.find("Text", self.namespace).text.strip(),
                "descriptionType": "Abstract",
            },
        )

    def visit_PublicationDate(self, node: Element) -> None:
        """Visit method for PublicationDate tag."""
        self.node["metadata"]["publicationYear"] = node.text[:4]

    def visit_RelatedWork(self, node: Element) -> None:
        """Visit method for RelatedWork tag."""

    def visit_RelationCode(self, node: Element) -> None:
        """Visit method for RelationCode tag."""

    def visit_RelatedProduct(self, node: Element) -> None:
        """Visit method for RelatedProduct tag."""

    def visit_BiographicalNote(self, node: Element) -> None:
        """Visit method for BiographicalNote tag."""


class DOISerialArticleWork(MedraVisitor):
    """DOISerialArticleWork class."""

    def visit_DOISerialArticleWork(self, node: Element) -> None:
        """Visit method for DOISerialArticleWork tag."""
        self.init_node()

        self.visit(node)

        self.node["metadata"]["types"] = {
            "resourceTypeGeneral": "DataPaper",
            "resourceType": "Article",
        }
        self.node["metadata"]["schemaVersion"] = "http://datacite.org/schema/kernel-4"
        self.node["metadata"]["identifiers"] = [
            {"identifierType": "DOI", "identifier": self.node["doi"]},
        ]

        self.nodes.append(self.node)

    def visit_SerialWork(self, node: Element) -> None:
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
    """DOISerialIssueWork class."""

    def init_node(self) -> None:
        """Init node."""
        super().init_node()
        self.node["metadata"] = {"creators": [{"name": ":none"}]}

    def visit_DOISerialIssueWork(self, node: Element) -> None:
        """Visit method for DOISerialIssueWork tag."""
        self.init_node()
        self.abstracts = []

        self.visit(node)

        for abstract in self.abstracts:
            self.append("descriptions", abstract)

        self.node["metadata"]["types"] = {
            "resourceTypeGeneral": "Collection",
            "resourceType": "Issue",
        }
        self.node["metadata"]["schemaVersion"] = "http://datacite.org/schema/kernel-4"
        self.node["metadata"]["identifiers"] = [
            {"identifierType": "DOI", "identifier": self.node["doi"]},
        ]

        self.nodes.append(self.node)

    def visit_WorkIdentifier(self, node: Element) -> None:
        """Visit method for WorkIdentifier tag."""
        if node.find("WorkIDType", self.namespace).text != "06":
            return

        self.append(
            "relatedIdentifiers",
            {
                "relatedIdentifier": node.find("IDValue", self.namespace).text,
                "relatedIdentifierType": "DOI",
                "relationType": "IsSupplementedBy",
            },
        )

    def visit_SerialWork(self, node: Element) -> None:
        """Visit method for SerialWork tag."""
        self.titles = []

        self.visit(node)

        self.node["metadata"]["titles"] = self.titles

    def visit_JournalIssue(self, node: Element) -> None:
        """Visit method for JournalIssue tag."""
        self.visit(node)

    def visit_JournalIssueDesignation(self, node: Element) -> None:
        """Visit method for JournalIsseDesignation tag."""
        self.append(
            "descriptions",
            {"description": node.text, "descriptionType": "SeriesInformation"},
        )

    def visit_RelatedWork(self, node: Element) -> None:
        """Visit method for RelatedWork tag."""
        self.visit(node)
