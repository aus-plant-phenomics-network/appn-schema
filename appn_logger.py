#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_logger.py
#
# Log issues that need to be drawn to the attention of administrators
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-09-10
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import logging
from enum import Enum
import textwrap
from typing import Optional
from appn_types import Issue, CompletionRuleType

### IssueMessage ##############################################################


class IssueMessage(str, Enum):
        """
        Class to hold a message describing an issue and an optional string 
        suggesting a fix.
        """
    suggested_fix: str

    def __new__(
        cls, message: str, suggested_fix: Optional[str] = None
    ) -> "IssueMessage":
        """
        Create the `IssueMessage` as a special string with an extra property 
        for the suggested fix.
        """
        obj = str.__new__(cls, message)
        obj._value_ = message
        obj.suggested_fix = suggested_fix
        return obj

    COMPLETION_RULE_MISSING_TYPE = (
        "No type was specified for a completion rule",
        f"Review YAML configuration file and add a valid value for 'type' to each rule, one of the following: {', '.join([rule.value for rule in CompletionRuleType])}",
    )
    COMPLETION_RULE_UNKNOWN_TYPE = (
        "Unrecognised type was specified for a completion rule",
        f"Review YAML configuration file and use a valid value for 'type' to each rule, one of the following: {', '.join([rule.value for rule in CompletionRuleType])}",
    )
    EXCEL_PATH_INVALID = "Invalid path to Excel spreadsheet"
    EXCEL_SHEET_INVALID = "Failed to read sheet from Excel spreadsheet"
    COLUMN_PROPERTY_NOT_SELECTED = (
        "Zero or multiple properties link the domain and range classes - cannot select a property for the column",
        "Add a domain_range_properties mapping to the YAML configuration file to specify the property to use for links between the domain and range classes. The domain class should be the outer key for the mapping, with the range class and the property as the key and value in the inner dictionary.",
    )
    NO_NAME_COLUMN_FOR_CLASS = (
        "No column identified as name for instances of APPN class in sheet"
    )
    SHEET_CONTAINS_DUPLICATE_NAMES = (
        "Sheet contains multiple rows with the same name",
        "Review sheet and ensure that no two rows share the same value for the name column",
    )
    SHEET_CONTAINS_DUPLICATE_EMBEDDED_NAMES = (
        "Multiple rows define class with the same name - ignoring all but first",
        "This relates to an embedded class. Repeated definitions may be expected. Otherwise review sheet and ensure that no two rows share the same value for the name column for the embedded class.",
    )
    MISSING_REFERENCE = (
        "Did not find expected definition for object referenced in a property",
        "Either add the referenced object to the appropriate sheet or correct the name where it is referenced.",
    )
    ADDED_LOCAL_PROPERTY = (
        "A spreadsheet column name did not match any defined property, so a new property was created in the vocabulary namespace.",
        "This only needs attention if it was unexpected. Check whether the column should have been mapped to a known property. Adding namespaces to the vocabulary_column_namespaces component of the YAML configuration allows properties from other namespaces to be included.",
    )
    RANGE_CLASS_NOT_SELECTED = (
        "A spreadsheet column name matches a property with more than one APPN schema class in its range, so values in the column could not be mapped to any referenced object.",
        "Add an property_range_classes mapping to the YAML configuration file to specify the class to be used for the property in the context of the domain class.",
    )


### IssueLogger ###############################################################


class IssueLogger:
    """
    Class to capture key notification messages in an issue log as well as in
    the Python logging outputs.
    """

    def __init__(self) -> None:
        """
        Prepare logger
        """
        self.issues: list[Issue] = []

        # Keep counts of issues by module and message
        self.module_counts: dict[str, int] = {}
        self.message_counts: dict[str | IssueMessage, int] = {}

    def log(
        self, level: int, module: str, message: str | IssueMessage, **properties: any
    ) -> None:
        """
        Save issue in list and log via logging.

        The message can be provided as an IssueMessage, which can include a 
        suggested fix, or as a plain text string. Keyword arguments are shared
        unchanged as a dictionary.

        :param level: Log level for `Issue`
        :param module: String identifier for module logging issue
        :param message: `IssueMessage` or text of message for issue
        :param properties: Dictionary of additional information to be logged
        """
        if isinstance(message, IssueMessage):
            message_string = message.value
        elif message in IssueMessage:
            message_string = IssueMessage[message].value
        else:
            message_string = str(message)
        issue = Issue(level, module, message_string, properties)
        if issue not in self.issues:
            self.issues.append(issue)
            if module not in self.module_counts:
                self.module_counts[module] = 1
            else:
                self.module_counts[module] = self.module_counts[module] + 1
            if message not in self.message_counts:
                self.message_counts[message] = 1
            else:
                self.message_counts[message] = self.message_counts[message] + 1
        logging.log(
            level,
            f"{message} ({'; '.join([f'module: {module}'] + [f'{k}: <{v}>' for k, v in properties.items()])})",
        )

    def list_issues(
        self,
        level: Optional[int] = None,
        module: Optional[str] = None,
        message: Optional[str] = None,
    ) -> list[Issue]:
        """
        Get list of recorded issues, optionally filtered by level and/or module name

        :param level: Log level for filtering issues (exact matches only)
        :param module: Module name for filtering issues (exact matches only)
        :return: List of `Issue`s
        """
        return [
            issue
            for issue in self.issues
            if (level is None or issue.level == level)
            and (module is None or issue.module == module)
            and (message is None or issue.message == message)
        ]

    def get_issue_counts_by_module(self) -> dict[str, int]:
        """
        Get dictionary storing counts of logged issues by module

        :return: Counts of issues by module
        """
        return self.module_counts

    def get_issue_counts_by_message(self) -> dict[str, int]:
        """
        Get dictionary storing counts of logged issues by message

        :return: Counts of issues by message
        """
        return self.message_counts

    def format_issues(self) -> str:
        """
        Return string with formatted information on all `Issues`.

        :return: Multiline string
        """
        report = ""
        for message, count in self.get_issue_counts_by_message().items():
            if len(report) > 0:
                report += "\n"
            report += f"ISSUE: {message.value if isinstance(message, IssueMessage) else message}\n"
            if isinstance(message, IssueMessage) and message.suggested_fix is not None:
                indent = " " * 17
                # The call to `strip` removes the initial indent so all aligns
                wrapped = "\n".join(textwrap.wrap(
                    message.suggested_fix, width = 120, initial_indent=indent, subsequent_indent=indent,
                )).strip()
                report += f"  SUGGESTED FIX: {wrapped}\n"
            report += f"  OCCURRENCES: {count}\n"
            index = 1
            issues = self.list_issues(message=message)
            key_length = max(
                [len(k) for issue in issues for k, v in issue.properties.items()]
            )
            for issue in issues:
                report += f"    {index:>3d} : {'\n          '.join([f'{k:{key_length}s} : {str(v)}' for k, v in issue.properties.items()])}\n"
                index += 1

        return report
