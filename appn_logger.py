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
from typing import Optional
from appn_types import Issue, CompletionRuleType

class IssueMessage(str, Enum):
    suggested_fix: str

    def __new__(
        cls, message: str, suggested_fix: Optional[str] = None
    ) -> Color:
        obj = str.__new__(cls, message)
        obj._value_ = message
        obj.suggested_fix = suggested_fix
        return obj

    COMPLETION_RULE_MISSING_TYPE = ("No type was specified for a completion rule", f"Review YAML configuration file and add a valid value for 'type' to each rule, one of the following: {', '.join([rule.value for rule in CompletionRuleType])}")
    COMPLETION_RULE_UNKNOWN_TYPE = ("Unrecognised type was specified for a completion rule", f"Review YAML configuration file and use a valid value for 'type' to each rule, one of the following: {', '.join([rule.value for rule in CompletionRuleType])}")
    EXCEL_PATH_INVALID = ("Invalid path to Excel spreadsheet")
    EXCEL_SHEET_INVALID = ("Failed to read sheet from Excel spreadsheet")
    COLUMN_PROPERTY_NOT_SELECTED = ("Zero or multiple properties link the domain and range classes - cannot select a property for the column", "Add a domain_range_properties mapping to the YAML configuration file to specify the property to use for links between the domain and range classes. The domain class should be the outer key for the mapping, with the range class and the property as the key and value in the inner dictionary.")
    NO_NAME_COLUMN_FOR_CLASS = ("No column identified as name for instances of APPN class in sheet")
    SHEET_CONTAINS_DUPLICATE_NAMES = ("Sheet contains multiple rows with the same name", "Review sheet and ensure that no two rows share the same value for the name column")
    SHEET_CONTAINS_DUPLICATE_EMBEDDED_NAMES = ("Multiple rows define class with the same name - ignoring all but first", "This relates to an embedded class. Repeated definitions may be expected. Otherwise review sheet and ensure that no two rows share the same value for the name column for the embedded class.")
    MISSING_REFERENCE = ("Did not find expected definition for object referenced in a property", "Either add the referenced object to the appropriate sheet or correct the name where it is referenced.")


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
        self.message_counts: dict[str|IssueMessage, int] = {}

    def log(self, level: int, module: str, message: str|IssueMessage, **properties: Any) -> None:
        """
        Save issue in list and log via logging
        
        :param level: Log level for `Issue`
        :param module: String identifier for module logging issue
        :param message: Text of message for issue
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
        logging.log(level, f"{message} ({'; '.join([f'module: {module}'] + [f'{k}: <{v}>' for k, v in properties.items()])})")

    def list_issues(self, level: Optional[int] = None, module: Optional[str] = None, message: Optional[str] = None) -> list[Issue]:
        """
        Get list of recorded issues, optionally filtered by level and/or module name
        
        :param level: Log level for filtering issues (exact matches only)
        :param module: Module name for filtering issues (exact matches only)
        :return: List of `Issue`s
        """
        return [issue for issue in self.issues if (level is None or issue.level == level) and (module is None or issue.module == module) and (message is None or issue.message == message)]

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