#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_parser.py - ExcelVocabularyParser
#
# Class for converting Excel spreadsheets into RDF vocabularies
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-09-03
# version ='2026.0.1'
# -----------------------------------------------------------------------------
import logging
import re
import warnings

import numpy as np
import pandas as pd

from pathlib import Path
from typing import Optional
from appn_types import Term, URIRefTriple, ColumnMapping, CompletionRuleType
from appn_dictionary import Dictionary
from appn_configuration import (
    APPN_VOCABULARY,
    APPN_VOCABULARY_ROOT,
    BIO_SCHEMA,
    CENTRAL_ORGANISATION,
    ConfigurationKey,
    DC_SCHEMA,
    DEFAULT_PREFIXES,
    ExplicitClassesFilter,
    RDF_SCHEMA,
    SCHEMA_SCHEMA,
    Configuration,
    Organisation,
    APPN_SCHEMA,
    SKOS_SCHEMA,
)
from appn_logger import IssueMessage
from rdflib import Graph, Namespace, URIRef, Literal

# Convenience versions of regularly used URIRefs 
rdf_type = URIRef(f"{RDF_SCHEMA}type")
rdf_property = URIRef(f"{RDF_SCHEMA}Property")
schema_domain_includes = URIRef(f"{SCHEMA_SCHEMA}domainIncludes")
schema_name = URIRef(f"{SCHEMA_SCHEMA}name")
schema_description = URIRef(f"{SCHEMA_SCHEMA}description")
skos_concept = URIRef(f"{SKOS_SCHEMA}Concept")
skos_concept_scheme = URIRef(f"{SKOS_SCHEMA}ConceptScheme")
skos_in_scheme = URIRef(f"{SKOS_SCHEMA}inScheme")
dc_title = URIRef(f"{DC_SCHEMA}title")
dc_description = URIRef(f"{DC_SCHEMA}description")

### ExcelVocabularyParser #####################################################

class ExcelVocabularyParser:
    """
    Parser class to parse Excel representations of the APPN-Schema-compliant
    term definitions from an APPN node and generate a corresponding rdflib `Graph`
    representation.

    The parser constructs a valid vocabulary of APPN Schema instances (doubling as
    SKOS concepts) for a specified APPN node or for common definitions shared
    across all APPN nodes. Each node vocabulary has its own namespace.

    The `load` method imports all recognised sheets from a supplied Excel 
    spreadsheet into the `Graph`.

    Multiple spreadsheets may consecutively be parsed into the same `Graph`. This
    is intended as a convenience so APPN nodes can manage definitions in the most
    convenient way. It is the responsibility of the user of this parser to ensure
    that all parsed spreadsheets relate to the same node.

    The parser scans each Excel spreadsheet for sheets with names that match the 
    (unqualified) name of an APPN schema class (e.g. "Trait", "GrowthFacility").

    The behaviour of the parser is controlled by the settings in a supplied
    `Configuration` object and by the content of a `Dictionary` object initialised
    using the `Configuration`. The `Dictionary` includes all definitions from the 
    APPN Schema and from the schemas it directly references and from the SKOS Core
    schema. Additionally, except in the case of the all-APPN vocabulary, the 
    `Dictionary` includes the current all-APPN vocabulary and preferentially 
    uses definitions it contains instead of creating new ones in the namespace of
    the node vocabulary.

    The first row in each such sheet is parsed as a set of references to RDF 
    properties or to another APPN schema class that is to be linked by a 
    predictable RDF property. The name in each cell is matched to a property using 
    the first matching strategy from the following:

    1. A property that includes the current schema class in its domain.

    2. A property from a namespace returned by the `get_vocabulary_column_namespaces`
       method of the `Configuration` instance. This is expected to include 
       schema.org, SKOS Core and Dublin Core, but others may be included.
    
    3. If the name in the cell matches another APPN Schema class name, a property
       that includes the current schema class in its domain and the matched class
       name in its range. (In this case, values in the column will be names of
       instances of the matched class). NOTE: At present, there are no ambiguous
       situations where multiple properties match these conditions, but this may
       change.
    
    4. If the `get_embedded_classes` method of the `Configuration` instance includes
       the name of an APPN Schema class that matches the start of the name in the 
       cell (with the first letter lowered), the remainder of name in the cell is
       processed as a candidate property for the matched class using steps 1 to 3.
       Any columns matching this rule are treated as a discrete set that could 
       have been specified in a separate sheet dedicated to the matching class. 
    
    5. A new property created in the namespace of the node vocabulary and specifying
       the current schema class as part of its domain.

    The parser accommodates repetition of the same property name in multiple 
    columns. Internally, it renames these temporarily as <property_name><integer> 
    so they can appear as discrete columns in a pandas DataFrame. During all later
    processing stages, the integer suffix is ignored.

    Each subsequent row in the sheet is parsed as an instance of the specified
    schema class. The instance receives an IRI constructed from an identifier for
    the APPN node and a normalised version of the value in a column associated 
    with the `schema:name` property. All non-blank cells are interpreted as the 
    object value (a `Literal` or a `URIRef`) for a triple relating to the 
    instance. If an instance of the class is already known with the same name
    (in any namespace, more specifically in the all-APPN vocabulary namespace),
    the new record is treated as a duplicate and ignored. Columns matched using
    step 4 above (i.e. via an "embedded class") are processed as though they 
    are in a separate sheet, but the "<embedded_class>Name" column is also used
    to create a property for the current schema class (using the logic in step
    3).

    Options from the `Configuration` allow the output to be tweaked in the 
    following ways:

        `Configuration`.`get_vocabulary_column_namespaces`:
            Determines which namespaces are searched to map column names to 
            properties.

        `Configuration`.`get_explicit_classes`: 
            Inserts additional `rdf:type` properties when an instance of a 
            specified class is created.

        `Configuration`.`get_excluded_classes`: 
            Excludes some classes from coarse selections by 
            `get_explicit_classes`.

        `Configuration`.`get_sheet_aliases`:
            Overrides the name of a sheet to match a desired APPN schema
            class

        `Configuration`.`get_column_aliases`: 
            Overrides the name of a column to match a different property

        `Configuration`.`get_completion_rules`: 
            Specifies additional processing for instances of an APPN 
            schema class
            
        `Configuration`.`get_class_abbreviations`: 
            Specifies short prefixes to use in IRIs of instances of specific 
            APPN schema classes

        `Configuration`.`get_property_expansions`:
            Specifies additional properties that should be added whenever
            a specified property is added

        `Configuration`.`get_embedded_classes`: 
            Lists classes that may appear as specified in step 4 above

        `Configuration`.`get_domain_range_properties`: 
            Get properties to use when linking primary class instances to
            embedded class instances

    The constructed `Graph` is separate from the `Graph` in the `Dictionary`
    of loaded schema assets. It is accessed using the `get_graph` method.

    Issues requiring the attention of a data administrator are stored using
    the `IssueLogger` in the `Configuration`.
    """

    def __init__(self, configuration: Configuration, node: Organisation) -> None:
        """
        Initialise parser to convert standard Excel spreadsheets into RDF vocabulary.

        :param configuration: Settings to control the processing of the spreadsheet.
        :param node: Definition of the APPN node (or APPN central office) for which the vocabulary is defined.
        """
        self.configuration = configuration
        self.node = node

        # The `IssueLogger` for messages to data administrators
        self.logger = configuration.get_logger()

        # The rdflib library generates a warning ("ConjunctiveGraph is deprecated, use Dataset instead")
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="rdflib")

        # The openpyxl library generates a warning ("Data Validation extension is not supported and will be removed")
        warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

        # Load schemas that provide key definitions. APPN_SCHEMA does not
        # directly reference SKOS, so SKOS_SCHEMA is separately loaded, but
        # others are imported based on their use in these two schemas.
        # For any vocabulary other than the central APPN vocabulary, load
        # the central vocabulary so its terms can be checked.
        self.dictionary = Dictionary(
            namespace_definitions=self.configuration.get_namespace_definitions()
        )
        self.dictionary.load(APPN_SCHEMA)
        self.dictionary.load(SKOS_SCHEMA)
        if node.id != CENTRAL_ORGANISATION:
            self.dictionary.load(APPN_VOCABULARY, asset_prefix=node.prefix)
        self.dictionary.import_references()

        # Cache local copies of configuration outputs
        self.sheet_aliases = configuration.get_sheet_aliases()
        self.column_aliases = configuration.get_column_aliases()
        self.class_abbreviations = configuration.get_class_abbreviations()
        self.property_expansions = configuration.get_property_expansions()
        self.embedded_classes = configuration.get_embedded_classes()
        self.domain_range_properties = configuration.get_domain_range_properties()

        # Cache for computed lists of superclasses to include for a specified
        # class
        self.explicit_classes: dict[URIRef, list[URIRef]]= {}

        # Dictionary for classes known from APPN schema (keyed by unqualified
        # name)
        self.appn_classes_by_name = {
            class_.name: class_
            for class_ in self.dictionary.list_classes(namespace=APPN_SCHEMA)
        }

        # Dictionary for classes known from APPN schema (keyed by unqualified
        # iri)
        self.appn_classes_by_iri = {
            class_.iri: class_
            for class_ in self.dictionary.list_classes(namespace=APPN_SCHEMA)
        }

        # Set to keep track of RDF objects already created
        self.instances: set[URIRef] = set()

        # A separate SKOS `ConceptScheme`` is created for the instances of each
        # APPN schema class. This maps the terms for the APPN classes to the
        # for the associated `ConceptScheme`
        self.concept_schemes: dict[Term, Term] = {}

        # Properties linking an APPN schema instance to another APPN schema
        # instance are set aside (as "required properties") until all sheets 
        # have been processed. This provides a simple way to detect and report
        # on any undefined terms.
        self.required_properties: list[URIRefTriple] = []

        # Definitions for new "local" properties (in the same namespace as the
        # generated RDF vocabulary) are deferred until a row is encountered 
        # that actually includes data for the property. This avoids the 
        # creation of properties that are never used.
        self.deferred_local_properties: dict[Term, list[Term]] = {}

        # External code should only access the vocabulary graph via the 
        # `get_graph` method which ensures that any processing for required
        # properties has been carried out
        self._graph = Graph()

        # Ensure the vocabulary graph uses the preferred namespace prefixes
        appn = self.configuration.get_appn()
        self._graph.bind(appn.prefix, appn.namespace, override=True)
        self._graph.bind(DEFAULT_PREFIXES[APPN_SCHEMA], Namespace(APPN_SCHEMA), override=True)
        self._graph.bind(DEFAULT_PREFIXES[BIO_SCHEMA], Namespace(BIO_SCHEMA))
        if self.node.id != CENTRAL_ORGANISATION:
            self._graph.bind(node.prefix, node.namespace)

        # Regular expression for replacing unwanted characters in IRIs
        self.name_pattern = re.compile(r"[\s'\"\\?;:,°*+(){}/\[\]-]+")

        # Regular expression for removing trailing integers added to column 
        # names to enable multiple columns to represent the same RDF property
        self.integer_stripper = re.compile(r"[0-9]*$")

    def load(self, excel_path: Path) -> bool:
        """
        Load APPN schema vocabulary terms from Excel spreadsheet.

        Identifies sheets with names matching the name of an APPN schema class OR
        mapped to an APPN schema class by `sheet_aliases` from the `Configuration`.

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :return: True if the spreadsheet was loaded without issues that need correction
        """
        if not excel_path.exists():
            self.logger.log(
                logging.ERROR,
                "ExcelVocabularyParser",
                IssueMessage.EXCEL_PATH_INVALID,
                EXCEL_PATH = excel_path
            )
            return False

        success = True

        for sheet in pd.ExcelFile(excel_path).sheet_names:

            # Process any sheet with a name matching an APPN schema class name OR
            # mapped to a class name using `sheet_aliases`
            sheet_class = (
                self.sheet_aliases[sheet] if sheet in self.sheet_aliases else sheet
            )
            if sheet_class in self.appn_classes_by_name:
                class_ = self.appn_classes_by_name[sheet_class]

                if not self.process_sheet(excel_path, sheet, class_):
                    success = False

        return success

    def process_sheet(self, excel_path: Path, sheet: str, sheet_class: Term) -> bool:
        """
        Load APPN schema vocabulary terms from single sheet of an Excel spreadsheet.

        Builds maps of the class instances that can be parsed from this sheet and then
        parses all available instances

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param sheet_class: `Term` for the main APPN schema class for which instances are to be generated
        :return: True if the sheet was loaded without issues that need correction
        """
        success = True

        # Read sheet with column headings as first row - this allows for multiple
        # columns for the same property to share the same heading
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        if df is None or len(df.index) == 0:
            self.logger.log(
                logging.ERROR, 
                "ExcelVocabularyParser", 
                IssueMessage.EXCEL_SHEET_INVALID, 
                EXCEL_PATH = excel_path, 
                EXCEL_SHEET = sheet)
            return False

        # Assign column names based on first row (and remove first row)
        df = self.fix_dataframe_columns(df)

        # Get a list of `Terms` for `embedded_classes` (from `Configuration`) - schema 
        # classes that may be "embedded" in a sheet for this `sheet_class`
        embeddings = []
        if sheet_class.name in self.embedded_classes:
            embeddable_classes = self.embedded_classes[sheet_class.name]
            for c in embeddable_classes:
                if c in self.appn_classes_by_name:
                    embeddings.append(self.appn_classes_by_name[c])

        # Build maps associating columns with RDF properties for the `sheet_class` and
        # any embedded classes, and process the sheet to extract instances based on
        # each of these maps
        for target_class, column_mappings in self.build_class_maps(
            excel_path, sheet, df, sheet_class, embeddings
        ).items():
            logging.debug(
                f"Mapping for: {target_class.curie}\n\n{''.join([f'  {m.column} --> {m.property} ({m.range_class.curie if m.range_class is not None else 'None'}, {m.primary_identifier})\n' for m in column_mappings])}"
            )
            if not self.parse_rows(excel_path, sheet, df, target_class, column_mappings):
                success = False

        return success

    def fix_dataframe_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Load APPN schema vocabulary terms from single sheet of an Excel spreadsheet.

        Interpret first row of dataframe as column names while allowing for some 
        columns to share the same name - these are mapped to columns with the name 
        suffixed with consecutive integers. Once the columns have been named, the 
        first row is discarded.

        :param df: `DataFrame` with unprocessed column headings in first row
        :return: `DataFrame` with columns renamed and first row removed
        """
        column_name_matches : dict[str, int] = {}
        columns : list[str] = []
        for heading in df.loc[0, :].values:
            column_name = self.integer_stripper.sub("", heading.strip())
            if column_name not in column_name_matches:
                column_name_matches[column_name] = 0
            else:
                column_name_matches[column_name] = column_name_matches[column_name] + 1
                column_name = f"{column_name}{column_name_matches[column_name]}"
            columns.append(column_name)
        df.columns = columns
        df = df.drop(0)
        return df

    def build_class_maps(
        self, 
        excel_path: Path,
        sheet: str,
        df: pd.DataFrame, 
        primary_class: Term, 
        embeddings: list[Term]
    ) -> dict[Term, list[ColumnMapping]]:
        """
        Provide mappings between column names and RDF properties

        Generates a list of column to property mappings for each of the classes 
        identified by `primary_class` or by `embeddings`

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param df: `DataFrame` to be mapped
        :param primary_class: `Term` for an APPN schema class for which all columns will be processed unless the column name is based on one of the embedded class names
        :param embeddings: list of `Term`s for APPN schema classes which may be included in the sheet via column names including a modified version of the class name
        :return: Dictionary mapping class `Term`s to lists of `appn_types`.`ColumnMapping` objects
        """
        class_maps: dict[Term, list[ColumnMapping]] = {}

        # For the primary class, map any column with a name starting with an 
        # empty string (i.e. all columns) unless the column name also starts
        # with a lower-first version of the name of one of the embedded classes
        # Any name of the form "<lower-first embedded class name>Name" is a 
        # special case and is mapped to "<embedded class name>" since this will
        # then be handled as a property with the primary class in its domain 
        # and the embedded class in its range
        class_map = self.build_class_map(
            excel_path, sheet, df, primary_class, "", [self.lower_first(e.name) for e in embeddings]
        )
        if class_map is not None:
            class_maps[primary_class] = class_map

        # For each embedding class, map only columns that start with a lower-first
        # version of the class name
        for embedding in embeddings:
            class_map = self.build_class_map(excel_path, sheet, df, embedding, self.lower_first(embedding.name), [])
            if class_map is not None:
                class_maps[embedding] = class_map

        return class_maps

    def build_class_map(
        self,
        excel_path: Path,
        sheet: str,
        df: pd.DataFrame,
        target_class: Term,
        required_prefix: str,
        excluded_prefixes: list[str],
    ) -> Optional[list[ColumnMapping]]:
        """
        Provide mappings between column names and RDF properties for a single 
        APPN schema class

        Generates a list of column to property mappings for `target_class`

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param df: `DataFrame` to be mapped
        :param target_class: `Term` for an APPN schema class for which the column mapping will be developed
        :param required_prefix: Only column names starting with this string will be processed
        :param excluded_prefixes: Column names starting with any of these strings will not be processed unless the remainder of the column name is "Name"
        :return: List of `appn_types`.`ColumnMapping` objects for any mapped columns or None if no columns have been mapped
        """

        # The `name_column` serves as the unique identifier for instances of this class
        # in this vocabulary - it is processed to generate the IRI for the instance
        name_column = self.lower_first(f"{required_prefix}Name")
        if name_column not in df.columns:
            logging.debug(
                f"Sheet does not include a name column {name_column} - ignoring sheet for class {target_class.curie}"
            )
            return None
        logging.debug(f"Handling rows as instances of {target_class.curie}")

        # Build dictionary of candidate properties for the class. Preference those with
        # the class as the domain, processing them in the returned order (which starts
        # with properties for the APPN class and proceeds up the superclass chain), and
        # then include in descending priority properties from schema.org, SKOS or Dublin
        # Core. If a property with the name has already been found, do not overwrite it.
        properties = {}

        # Columns will be handled as properties which include the current class as their
        # domain. If no such property exists with the specified name, a matching
        # will be selected from one of the namespaces specified in the configuration
        # (in descending order of precedence). This code builds a map of unqualified
        # property names to the preferred property. A clean map is created for each
        # sheet in the spreadsheet since the domain properties vary by class.
        for p in self.dictionary.list_domain_properties_for_class(target_class.iri):
            if p.name not in properties:
                properties[p.name] = p
        for s in self.configuration.get_vocabulary_column_namespaces():
            for p in self.dictionary.list_properties(namespace=s):
                if p.name not in properties:
                    properties[p.name] = p

        # Build dictionary of property URIRefs for each column.
        column_mappings = []

        # Map each relevant column name to a property
        for column in df.columns:
            if column.startswith(required_prefix):
                # column_name will be manipulated to get the name for the 
                # property
                column_name = column

                # Exclude any columns with names starting with an excluded
                # prefix EXCEPT for columns with names of the form 
                # "<excluded_prefix>Name" - these should be treated as 
                # properties linking to an instance of the specified class.
                ignore_column = False
                for excluded_prefix in excluded_prefixes:
                    if column_name.startswith(excluded_prefix):
                        if column_name == f"{excluded_prefix}Name":
                            column_name = self.upper_first(excluded_prefix)
                        else:
                            ignore_column = True
                            break
                if not ignore_column:
                    # Remove any integer suffix present in the Excel spreadsheet
                    column_name = self.integer_stripper.sub("", column_name .strip())

                    # Remove any required prefix and lower the first letter of the
                    # remainder to get the name for the property
                    if (
                        len(required_prefix) > 0
                        and column_name.startswith(required_prefix)
                    ):
                        column_name = self.lower_first(column_name[len(required_prefix) :])

                    # `Configuration` may supply `column_aliases` to override how this
                    # column is to be processed
                    if column_name in self.column_aliases:
                        column_name = self.column_aliases[column_name]

                    # This column will be mapped to the `URIRef` for a property
                    column_property = None

                    # If the object of the triples represented by this column is expected 
                    # to be a class instance, record the expected class
                    related_class = None

                    # The simple case is when the column name matches a property already
                    # identified for this class
                    if column_name in properties:
                        column_property = URIRef(properties[column_name].iri)

                    # Otherwise, if the column name matches the name of an APPN schema
                    # class, the column should be mapped to a property including the
                    # correct classes in the domain and range
                    elif column_name in self.appn_classes_by_name:
                        related_class = self.appn_classes_by_name[column_name]
                        # A property may be specified in the `Configuration`
                        if target_class.name in self.domain_range_properties and related_class.name in self.domain_range_properties[target_class.name]:
                            column_property = URIRef(self.domain_range_properties[target_class.name][related_class.name])
                        # Otherwise try to find a unique match based on domain and range
                        else:
                            range_properties = (
                                self.dictionary.list_properties_by_domain_and_range(
                                    target_class.iri,
                                    related_class.iri,
                                    namespace=APPN_SCHEMA,
                                )
                            )
                            if len(range_properties) == 1:
                                column_property = URIRef(range_properties[0].iri)
                        if column_property is None:
                            # Notify the data administrator to add configuration settings.
                            self.logger.log(logging.ERROR, "ExcelVocabularyParser", 
                                IssueMessage.COLUMN_PROPERTY_NOT_SELECTED, 
                                EXCEL_PATH=excel_path, 
                                EXCEL_SHEET=sheet, 
                                EXCEL_COLUMN_NAME=column,
                                DOMAIN_APPN_CLASS=target_class.curie,
                                RANGE_APPN_CLASS=related_class.curie 
                            )
                            related_class = None

                    # If no matching property has been identified, define one for creation
                    # when required
                    if column_property is None:

                        # Local properties are those that do not exist in the `Dictionary` and that
                        # therefore need to be defined with the vocabulary - defer creating the 
                        # property until a row contains an actual value for it
                        is_local_property = True

                        column_property = URIRef(
                            f"{APPN_VOCABULARY_ROOT}{self.node.id}/{self.lower_first(column_name)}"
                        )
                        is_local_property = True
                        if column_property not in self.deferred_local_properties:
                            self.deferred_local_properties[column_property] = []
                        self.deferred_local_properties[column_property].append(target_class)
                    else:
                        is_local_property = False

                    logging.info(f"Column {column} recognised as {str(column_property)} for class {target_class.curie}")

                    column_mappings.append(
                        ColumnMapping(
                            column,
                            column_property,
                            related_class,
                            column == name_column,
                            is_local_property,
                        )
                    )
        return column_mappings if len(column_mappings) > 0 else None

    def parse_rows(
        self, excel_path, sheet, df: pd.DataFrame, target_class: Term, column_mappings: list[ColumnMapping]
    ) -> bool:
        """
        Generate APPN schema class instances from `DataFrame` loaded from Excel spreadsheet

        Uses supplied column mappings and `Configuration` settings to generate class instances
        as RDF triples

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param df: `DataFrame` to be processed
        :param target_class: `Term` for APPN schema class for instances to generate
        :param column_mappings: List of `ColumnMapping` objects for mapped columns
        :return: True if the sheet was processed without issues that need correction
        """
        success = True

        # Find the column that will be used for constructing IRIs (and hence which will
        # need to hold unique values)
        name_column = None
        for mapping in column_mappings:
            if mapping.primary_identifier:
                name_column = mapping.column
                break
        if name_column is None:
            self.logger.log(
                logging.ERROR, 
                "ExcelVocabularyParser", 
                IssueMessage.NO_NAME_COLUMN_FOR_CLASS,
                EXCEL_PATH=excel_path, 
                EXCEL_SHEET=sheet, 
                APPN_CLASS=target_class.curie,
            )
            return False

        # Process all rows with values in the name_column column
        for index, row in df.iterrows():
            if row[name_column] not in [np.nan, None, ""]:
                name = str(row[name_column])

                # Only proceed if this vocabulary is for the central organisation
                # or if the given name does not already exist among instances of
                # this class in the vocabulary for the central organisation.
                # Central definitions override node definitions.
                if (
                    self.node.id == CENTRAL_ORGANISATION
                    or len(
                        self.dictionary.list_instances_by_class_and_name(
                            target_class, name, namespace=APPN_VOCABULARY
                        )
                    )
                    == 0
                ):
                    if not self.add_instance(
                        excel_path, sheet, index, row, target_class, name_column, name, column_mappings):
                        success = False

        return success

    def add_instance(self, excel_path: Path, sheet: str, index: int, row: pd.Series, target_class: Term, name_column: str, name: str, column_mappings: list[ColumnMapping]) -> bool:
        """
        Generate triples from a spreadsheet row

        Generates an IRI and specifies its types, processes all `ColumnMapping`s
        for this row, notes any related class instances that are expected before 
        processing is complete, and runs any completion rules defined in the
        `Configuration`

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param row: `Series` (i.e row) to be processed as an instance defined by a set of RDF triples
        :param target_class: `Term` for APPN schema class for instances to generate
        :param name_column: the name of the column in the `Series` that contains the name for the instance
        :param name: the name for the instance
        :param column_mappings: List of `ColumnMapping` objects for mapped columns
        :return: True if the row was processed without issues that need correction
        """
        # The IRI for this instance is based on the node, the class and the name
        iri = self.get_iri(target_class.name, name)
        if iri in self.instances:
            # We already have a defined instance with this IRI. 
            # 
            # If the instance comes from a sheet dedicated to the class 
            # (in which case the name_column will simply be "name"), log
            # a failure. 
            #
            # Otherwise, warn that only the first definition will be used.
            # NOTE: It would be possible to compare the rows in question
            # and only report a warning if they are different, but this
            # approach allows a user to leave all columns blank in the 
            # second and subsequent references.
            if name_column == "name":
                self.logger.log(
                    logging.ERROR, 
                    "ExcelVocabularyParser", 
                    IssueMessage.SHEET_CONTAINS_DUPLICATE_NAMES,
                    EXCEL_PATH=excel_path, 
                    EXCEL_SHEET=sheet, 
                    EXCEL_ROW=str(index + 2),
                    EXCEL_COLUMN=name_column,
                    APPN_CLASS=target_class.curie,
                    NAME=name,
                )
                return False
            else:
                self.logger.log(
                    logging.INFO, 
                    "ExcelVocabularyParser", 
                    IssueMessage.SHEET_CONTAINS_DUPLICATE_EMBEDDED_NAMES,
                    EXCEL_PATH=excel_path, 
                    EXCEL_SHEET=sheet, 
                    EXCEL_ROW=str(index + 2),
                    EXCEL_COLUMN=name_column,
                    APPN_CLASS=target_class.curie,
                    NAME=name,
                )
                return True

        success = True

        # Add the type statements for the IRI to the graph and put it in a `ConceptScheme`       
        term = self.insert_instance(URIRef(target_class.iri), iri, True)

        # Add properties for each mapped column with a non-null value
        for column_mapping in column_mappings:
            value = row[column_mapping.column]
            if value not in [np.nan, None, ""]:
                property_term = column_mapping.property

                # Locally defined properties are only added as the first triple is 
                # created using the property
                if (
                    column_mapping.is_local_property
                    and property_term in self.deferred_local_properties
                ):
                    self.add_local_property(
                        excel_path,
                        sheet,
                        property_term,
                        column_mapping.column,
                        self.deferred_local_properties[property_term],
                    )
                    self.deferred_local_properties.pop(property_term)

                # For properties with a class instance as the expected range, the
                # value in the column will be the name of a class instance, either in
                # the current namespace or in the APPN central namespace.
                if column_mapping.range_class is not None:

                    # If a centrally defined instance exists with this name, the triple 
                    # should reference it.
                    matching_term = None
                    if self.node.id != CENTRAL_ORGANISATION:
                        matching_terms = self.dictionary.list_instances_by_class_and_name(
                            column_mapping.range_class, str(value), namespace=APPN_VOCABULARY,
                        )
                        if len(matching_terms) > 0:
                            matching_term = URIRef(matching_terms[0].iri)
                            self.add_triple(term, property_term, matching_term)
                    
                    # If there is no centrally defined instance, document the fact that
                    # we expect such an instance to be created. By deferring the addition
                    # of the triple for this column, we are able to report any missing
                    # instances that are expected.
                    if matching_term is None:
                        self.required_properties.append(
                            URIRefTriple(
                                term,
                                property_term,
                                self.get_iri(column_mapping.range_class.name, str(value))
                            )
                        )
                else:
                    # For all properties that do not have a range class, create a new
                    # triple with a URIRef or Literal value
                    if isinstance(value, str) and value.startswith("http"):
                        value_term = URIRef(value.strip())
                    else:
                        value_term = Literal(value)
                    self.add_triple(term, property_term, value_term)

        # Get any rules from the `Configuration` for completing instances of this class 
        # and process these by type.
        completion_rules = self.configuration.get_completion_rules(target_class.name)
        if len(completion_rules) > 0:
            existing_properties = [str(p) for s, p, o in self._graph if s == term]
            for desired_property, rule in completion_rules.items():
                # Current rules are expected to fire only of no instance of the desired
                # property is found - this could be controlled by additional rule 
                # properties
                if desired_property not in existing_properties:
                    if "type" not in rule:
                        self.logger.log(logging.ERROR, "Configuration", IssueMessage.COMPLETION_RULE_MISSING_TYPE,
                            CONFIGURATION_FILE = self.configuration.configuration_filepath,
                            CONFIGURATION_KEY = ConfigurationKey.COMPLETION_RULES,
                            APPN_SCHEMA_CLASS = target_class.curie,
                            TARGET_PROPERTY = desired_property,
                        )
                        success = False
                    elif rule["type"] == CompletionRuleType.REFLEXIVE.value:
                        # Rules with the type "reflexive" indicate that the term should have
                        # a reflexive property linking it to itself.
                        logging.debug(f"Completing term {term} with property {desired_property} using rule {rule}")
                        self.add_triple(term, URIRef(desired_property), term)
                    else:
                        self.logger.log(logging.ERROR, "Configuration", IssueMessage.COMPLETION_RULE_UNKNOWN_TYPE,
                            CONFIGURATION_FILE = self.configuration.configuration_filepath,
                            CONFIGURATION_KEY = ConfigurationKey.COMPLETION_RULES,
                            APPN_SCHEMA_CLASS = target_class.curie,
                            TARGET_PROPERTY = desired_property,
                            COMPLETION_RULE_TYPE = rule["type"]
                        )
                        success = False

        return success 


    def insert_instance(
        self, main_class: URIRef, iri: URIRef, is_concept: Optional[bool] = False
    ) -> URIRef:
        """
        Add an IRI to the graph

        Inserts type statements (including superclasses specified in the `Configuration`)
        for an IRI and optionally adds it to a SKOS ConceptScheme

        :param main_class: `Term` for APPN schema class for instance identified by IRI
        :param iri: the name of the column in the `Series` that contains the name for the instance
        :param is_concept: If True, the IRI will be added to a SKOS ConceptScheme 
            associated with the main_class
        :return: The inserted IRI
        """
        # Avoid adding the instance multiple times
        if iri in self.instances:
            return iri
        
        # Add type statements for the main class and any superclasses specified by the
        # `Configuration` (and `skos:Concept` if `is_concept` is True).
        for instance_class in self.list_explicit_classes(main_class, is_concept):
            self._graph.add((iri, rdf_type, instance_class))

        # Add any `Concept` to a corresponding `ConceptScheme`
        if is_concept:
            if main_class not in self.concept_schemes:
                self.add_concept_scheme(main_class)
            self._graph.add((iri, skos_in_scheme, self.concept_schemes[main_class]))

        self.instances.add(iri)

        return iri

    def add_concept_scheme(self, main_class: URIRef) -> URIRef:
        """
        Add triples defining a SKOS `ConceptScheme`

        Inserts an IRI with type skos:ConceptScheme and gives it a name and description.

        :param main_class: `Term` for APPN schema class for instances associated with `ConceptScheme`
        :return: The concept scheme IRI
        """
        # Avoid adding the scheme multiple times

        if main_class in self.concept_schemes:
            return self.concept_schemes[main_class]

        if str(main_class) in self.appn_classes_by_iri:
            class_name = self.appn_classes_by_iri[str(main_class)].name
        else:
            class_name = str(main_class)
        concept_scheme_term = self.get_iri("ConceptScheme", class_name)
        self.insert_instance(skos_concept_scheme, concept_scheme_term)
        self.add_triple(concept_scheme_term, schema_name, Literal(class_name))
        self.add_triple(concept_scheme_term, schema_description, Literal(
            f"Concept scheme including instances of the {class_name} class from the APPN {self.node.id} node"
        ))

        self.concept_schemes[main_class] = concept_scheme_term
        
        return concept_scheme_term


    def list_explicit_classes(
        self, main_class_iri: URIRef, is_concept: Optional[bool] = False
    ) -> list[URIRef]:
        """
        Build list of classes (`rdf:type` values) to define for an instance of
        the given class.

        The `Configuration` can specify superclasses that should automatically 
        be inserted, and skos:Concept is included for all vocabulary terms.

        :param main_class: `URIRef` for APPN schema class
        :param is_concept: True if `skos:Concept` should be included
        :return: List of IRIs for matching superclasses
        """
        main_class = str(main_class_iri)

        # `explicit_classes` is a cache to minimise redundant calculations
        key = f"{main_class}|{is_concept}"
        if key in self.explicit_classes:
            return self.explicit_classes[key]

        # Get list of all known classes in inheritance hierarchy for 
        # this class (including the class itself)
        superclasses = self.dictionary.list_superclasses(main_class)

        # Rules determining which superclasses should be added
        explicit_rules = self.configuration.get_explicit_classes()

        # Filters to over rile explicit rules
        excluded_classes = self.configuration.get_excluded_classes()

        explicit_classes = []

        for superclass in superclasses:
            if superclass.iri == main_class:
                # Always include the class itself
                explicit_classes.append(main_class_iri)
            elif (
                superclass.ns in explicit_rules
                and superclass.iri not in excluded_classes
            ):
                rule = explicit_rules[superclass.ns]
                if isinstance(rule, list):
                    # Include any class explicitly referenced by a rule
                    if superclass.name in rule:
                        explicit_classes.append(URIRef(superclass.iri))
                elif isinstance(rule, str):
                    if rule == ExplicitClassesFilter.ALL.value:
                        # Include all classes matching an "all" rule
                        explicit_classes.append(URIRef(superclass.iri))
                    elif rule == ExplicitClassesFilter.FIRST.value:
                        # Match only the first class matching a "first" rule
                        explicit_classes.append(URIRef(superclass.iri))

                        # Remove the rule so we don't add more matches
                        # NOTE - every call to configuration.get_explicit_classes returns
                        # a new copy, so popping the value is safe.
                        explicit_rules.pop(superclass.ns)

        if is_concept:
            # This IRI is also a SKOS Concept
            explicit_classes.append(skos_concept)

        # Remenber this list
        self.explicit_classes[key] = explicit_classes

        return explicit_classes

    def add_triple(self, subject: URIRef, property: URIRef, object: URIRef|Literal) -> None:
        """
        Add a triple to the graph with any specified additions

        Insert the requested triple, plus additional triples for any properties
        indicated by the `property_expansion` from the `Configuration`

        :param subject: The subject for the triple
        :param property: The main property for the triple
        :param object: The object for the triple
        """
        self._graph.add((subject, property, object))

        # If specified, add extra properties with the same object
        if property in self.property_expansions:
            for expansion_property in self.property_expansions[property]:
                self._graph.add((subject, expansion_property, object))

    def add_local_property(
        self, excel_path: Path, sheet: str, iri: URIRef, name: str, domain_classes: list[Term]
    ) -> None:
        """
        Add a new RDF `Property` to the graph in the current namespace

        Create the property with the supplied name and domain classes.

        :param excel_path: Location of a vocabulary stored as a multi-sheet Excel spreadsheet
        :param sheet: Name of the sheet to be processed
        :param property: IRI for the property
        :param name: Name for the property
        :param domain_classes: List of classes to be included in the property domain
        """
        self.insert_instance(rdf_property, iri)
        self.add_triple(iri, schema_name, Literal(name))
        for domain_class in domain_classes:
            self._graph.add((iri, schema_domain_includes, URIRef(domain_class.iri)))
        self.logger.log(
            logging.INFO,
            "ExcelVocabularyParser",
            IssueMessage.ADDED_LOCAL_PROPERTY,
            EXCEL_PATH=excel_path,
            EXCEL_SHEET=sheet,
            EXCEL_COLUMN=name,
            DOMAIN_CLASSES=", ".join([class_.curie for class_ in domain_classes]),
            NEW_LOCAL_PROPERTY=iri
        )

    def get_graph(self) -> Graph:
        """
        Access the `Graph` created from the spreadsheets.

        Ensure the graph is fully processed and return it

        :return: Graph
        """
        logging.debug(f"Finalising and returning graph")

        if len(self.required_properties) > 0:
            self.process_required_properties()

        return self._graph

    def process_required_properties(self) -> bool:
        """
        Process all deferred required properties.

        Check that all expected terms exist and add any outstanding
        triples referencing them.

        :return: True if all properties have been processed
        """
        success = True

        logging.debug(f"Processing {len(self.required_properties)} properties")

        remaining = []
        for required_property in self.required_properties:
            logging.debug(f"Processing required property {required_property}")
            if required_property.object in self.instances:
                # If the object exists in the graph, add the triple
                self._graph.add(
                    (
                        required_property.subject,
                        required_property.property,
                        required_property.object,
                    )
                )
            else:
                # If the object does not exist, report and error and remember
                # the triple
                self.logger.log(
                    logging.ERROR, 
                    "ExcelVocabularyParser", 
                    IssueMessage.MISSING_REFERENCE,
                    SUBJECT_TERM = str(required_property.subject),
                    PROPERTY_TERM = str(required_property.property),
                    MISSING_OBJECT_TERM = str(required_property.object),
                )
                remaining.append(required_property)
                success = False

        logging.debug(f"{len(remaining)} properties unprocessed")
        self.required_properties = remaining

        return success

    def get_iri(self, class_name: str, name: str) -> URIRef:
        """
        Generate an IRI for an instance of a class in the current namespace and with the given name

        Converts an instance name to a safe IRI. The IRI has the pattern 
        "<APPN_VOCABULARY_ROOT><node>/<class_identifier>_<name>".

        :param class_name: String name for the APPN schema class
        :param name: Name to be used in constructing the IRI
        :return: Constructed IRI
        """
        # Convert name to a safe TitleCase form
        clean_name = "".join(
            [w.title() for w in self.name_pattern.sub(" ", name).strip().split()]
        )
        
        # Use any abbreviation for the class from the `Configuration`
        class_name = (
            self.class_abbreviations[class_name] if class_name in self.class_abbreviations else class_name
        ).lower()

        # Build and return the IRI
        return URIRef(f"{APPN_VOCABULARY_ROOT}{self.node.id}/{class_name}_{clean_name}")

    def lower_first(self, name: str) -> str:
        """
        Return name string with first character wrapped to lower case

        :param name: Name for processing
        :return: Name with first character in lowercase
        """
        return name[0].lower() + name[1:]

    def upper_first(self, name: str) -> str:
        """
        Return name string with first character wrapped to upper case

        :param name: Name for processing
        :return: Name with first character in uppercase
        """
        return name[0].upper() + name[1:]
