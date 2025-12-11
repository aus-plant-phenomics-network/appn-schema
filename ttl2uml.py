"""
Python script to generate PlantUML diagrams from the appn-schema.ttl model.

Author: Donald Hobern
"""

import sys
import re
import logging
import os
import io

# Set up logfile
logfile_name = "ttl2uml.log"
logging.basicConfig(filename=logfile_name, filemode="w", level=logging.INFO, format='%(asctime)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
logging.getLogger().addHandler(logging.StreamHandler())

# Name of turtle input file
ttl_file = "appn-schema.ttl"

# Output folders
uml_folder = "ttl_uml"
if not os.path.exists(uml_folder):
    os.mkdir(uml_folder)
markdown_folder = "doc"
if not os.path.exists(markdown_folder):
    os.mkdir(markdown_folder)

# Colours for random selection to colour classes from different packages (keyed on prefix)
colours = [
    "#FFDDDD",
    "#DDFFDD",
    "#DDDDFF",
    "#EEFFCC",
    "#FFCCEE",
    "#CCEEFF",
    "#EECCFF",
    "#FFEECC",
    "#CCFFEE",
]

# Packages can be excluded from the main diagram by providing prefix names with a leading minus symbol.
# If any exclusions are specified, only the pruned main diagram is generated.
# Otherwise, the complete main diagram and individal diagrams centred on each APPN class are generated.
exclusions = []
for arg in sys.argv[1:]:
    if arg.startswith("-"):
        exclusions.append(arg[1:])

# Patterns for filtering rows in turtle file - note that these are very restrictive.
pattern_prefix = re.compile(r"^@prefix (\w+): <(.*)>[ \.;]*$")
pattern_class = re.compile(r"^(\w+):(\w+) a rdfs:Class[ \.;]*$")
pattern_subclass = re.compile(r"^\s* rdfs:subClassOf (\w+):(\w+)[ \.;]*$")
pattern_property = re.compile(r"^(\w+):(\w+) a rdfs:Property[ \.;]*$")
pattern_subproperty = re.compile(r"^\s*rdfs:subPropertyOf (\w+):(\w+)[ \.;]*$")
pattern_domain = re.compile(r"^\s*schema:domainIncludes ([\w,:]+)[ \.;]*$")
pattern_range = re.compile(r"^\s*schema:rangeIncludes ([\w,:]+)[ \.;]*$")
pattern_comment = re.compile(r'^\s*rdfs:comment "([^"]*)"[ \.;]*$')

# State objects to store data needed for diagrams
prefixes = {}
packages = {}
inheritance = {}
properties = {}
property_inheritance = {}
package_colours = {}
context_item = None
comments = {}

# Establish container for classes from an identified package and associate the package with a colour.
def get_package(p: str) -> dict[str, list[tuple[str,str]]]:
    if p not in prefixes:
        logging.error(f"Prefix {p} is undefined")
    if p not in packages:
        package_colours[p] = colours[len(package_colours)]
        packages[p] = [] 
    return packages[p]

# Add a class to an identified package
def get_class(p: str, c: str) -> tuple[str,str]:
    package = get_package(p)
    cls = (p, c)
    if cls not in package:
        package.append(cls)
    return cls

# Record a subclass
def add_inheritance(child: tuple[str,str], parent: tuple[str,str]) -> None:
    if child not in inheritance:
        inheritance[child] = [parent]
    else:
        inheritance[child].append(parent)

# Get an existing property definition or set up a placeholder - the lists are for domain and range
# classes.
def get_property(p: str, pp: str) -> tuple[str,str]:
    pty = (p, pp)
    if pty not in properties:
        properties[pty] = ([], [])
    return pty

# Record a subproperty
def add_property_inheritance(child: tuple[str,str], parent: tuple[str,str]) -> None:
    if child not in property_inheritance:
        property_inheritance[child] = [parent]
    else:
        property_inheritance[child].append(parent)

# Add domains to a property
def add_domain(pty: tuple[str,str], domain_classes: str) -> None:
    ppty = get_property(pty[0], pty[1])
    for cls in domain_classes.split(","):
        prefix, c = cls.split(":")
        domain = (prefix, c)
        property = properties[ppty]
        if domain not in property[0]:
            property[0].append(domain)

# Add ranges to a property
def add_range(pty: tuple[str,str], range_classes: str) -> None:
    ppty = get_property(pty[0], pty[1])
    for cls in range_classes.split(","):
        prefix, c = cls.split(":")
        range = (prefix, c)
        property = properties[ppty]
        if range not in property[1]:
            property[1].append(range)

# Add comments to an item
def add_comment(item: tuple[str,str], comment: str) -> None:
    if item in comments:
        c = comments.get(item)
        comments[item] = f"{c}\n\n{comment}"
    else:
        comments[item] = comment

# Get formatted name for a class/property tuple.
def get_name(parts: tuple[str:str]) -> str:
    return parts[1] if parts[0] == "appn" else f'"{parts[0]}:{parts[1]}"'

# Generate UML property definitions for a specified class
def write_properties(uml: io.TextIOWrapper, md: io.TextIOWrapper, cls: tuple[str, str], focus_class: tuple[str,str], heading_written: bool) -> bool:
    class_name = get_name(cls)
    reflexive = False
    for ppty in properties:
        ppty_name = get_name(ppty)
        property = properties[ppty]
        if cls in property[0]:
            if not heading_written:
                md.write(f"## Properties\n")
                heading_written = True
            if len(property[1]) == 0:
                if cls == focus_class:
                    uml.write(f"class {class_name} #line.bold {{\n    {ppty_name}\n}}\n")
                else:
                    uml.write(f"class {class_name} #line.bold {{\n    {ppty_name}\n}}\n")
                md.write(f"* {focus_class[1]} {prefixes[ppty[0]]}{ppty[1]}\n")
            for r in property[1]:
                if r == cls:
                    reflexive = True
                r_name = get_name(r)
                if r != focus_class:
                    package_colour = "" if r[0] == "appn" else package_colours[r[0]]
                    uml.write(f"class {r_name} {package_colour}\n")
                uml.write(f"{class_name} --> {r_name} : {ppty_name}\n")
                if cls == focus_class:
                    this_class = f"{focus_class[0]}:{focus_class[1]}"
                elif cls[0] == "appn":
                    this_class = f"[appn:{cls[1]}](/doc/appn_{cls[1]}.md)"
                else:
                    expanded_r = f"{prefixes[cls[0]]}{cls[1]}"
                    this_class = f"[{cls[0]}:{cls[1]}]({expanded_r})"
                if r[0] == "appn":
                    other_class = f"[appn:{r[1]}](/doc/appn_{r[1]}.md)"
                else:
                    other_class = f"[{r[0]}:{r[1]}]({prefixes[r[0]]}{r[1]})"
                if ppty in comments:
                    md.write(f"* {this_class} **{ppty[0]}:{ppty[1]}** {other_class}\n    * {comments[ppty]}\n")
                else:
                    md.write(f"* {this_class} **{ppty[0]}:{ppty[1]}** {other_class}\n")
        if cls in property[1]:
            for r in property[0]:
                if not heading_written:
                    md.write(f"## Properties\n")
                    heading_written = True
                if r != cls or not reflexive:
                    r_name = get_name(r)
                    if r != focus_class:
                        package_colour = "" if r[0] == "appn" else package_colours[r[0]]
                        uml.write(f"class {r_name} {package_colour}\n")
                    uml.write(f"{r_name} --> {class_name} : {ppty_name}\n")
                    if cls == focus_class:
                        this_class = f"{focus_class[0]}:{focus_class[1]}"
                    elif cls[0] == "appn":
                        this_class = f"[{cls[0]}:{cls[1]}](/doc/appn_{cls[1]}.md)"
                    else:
                        expanded_r = f"{prefixes[cls[0]]}{cls[1]}"
                        this_class = f"[{cls[0]}:{cls[1]}]({expanded_r})"
                    if r[0] == "appn":
                        other_class = f"[appn:{r[1]}](/doc/appn_{r[1]}.md)"
                    else:
                        other_class = f"{prefixes[r[0]]}{r[1]}"
                    if ppty in comments:
                        md.write(f"* {other_class} **{ppty[0]}:{ppty[1]}** {this_class}\n    * {comments[ppty]}\n")
                    else:
                        md.write(f"* {other_class} **{ppty[0]}:{ppty[1]}** {this_class}\n")
    
    if cls in inheritance:
        for parent in inheritance[cls]:
            heading_written = write_properties(uml, md, parent, focus_class, heading_written)
    
    return heading_written

# Generate UML superclass definitions for a specified class - this writes the class too.
def write_parents(uml: io.TextIOWrapper, md: io.TextIOWrapper, cls: tuple, focus_class: tuple[str,str]) -> str:
    class_name = get_name(cls)
    package_colour = "" if cls[0] == "appn" else package_colours[cls[0]]
    style = "#line.bold" if cls == focus_class else ""
    uml.write(f"class {class_name} {package_colour} {style}\n")
    if cls in inheritance:
        for parent in inheritance[cls]:
            if parent[0] == "appn":
                md.write(f"* [{prefixes[parent[0]]}{parent[1]}](/doc/appn_{parent[1]}.md)\n")
            else:
                md.write(f"* {prefixes[parent[0]]}{parent[1]}\n")
            parent_name = write_parents(uml, md, parent, focus_class)
            uml.write(f"{class_name} --|> {parent_name}\n")
    return class_name

# Generate UML subclass definitions for a specified class - this writes the class too.
def write_children(uml: io.TextIOWrapper, md: io.TextIOWrapper, cls: tuple[str,str], focus_class: tuple[str,str]) -> str:
    class_name = get_name(cls)
    if cls != focus_class:
        package_colour = "" if cls[0] == "appn" else package_colours[cls[0]]
        uml.write(f"class {class_name} {package_colour}\n")
        if cls[0] == "appn":
            md.write(f"* [{prefixes[cls[0]]}{cls[1]}](/doc/appn_{cls[1]}.md)\n")
        else:
            md.write(f"* {prefixes[cls[0]]}{cls[1]}\n")
    heading_written = False
    for child in inheritance:
        if cls in inheritance[child]:
            if cls == focus_class and not heading_written:
                md_file.write(f"## Subclasses\n")
                heading_written = True
            child_name = write_children(uml, md, child, focus_class)
            uml.write(f"{child_name} --|> {class_name}\n")
    return class_name

# Parse the turtle
with open(ttl_file) as f:
    for line in f:
        if (match := pattern_prefix.match(line)) is not None:
            prefixes[match.group(1)] = match.group(2)
        elif (match := pattern_class.match(line)) is not None:
            context_item = get_class(match.group(1), match.group(2))
        elif (match := pattern_subclass.match(line)) is not None:
            parent_class = get_class(match.group(1), match.group(2))
            add_inheritance(context_item, parent_class)
        elif (match := pattern_property.match(line)) is not None:
            context_item = get_property(match.group(1), match.group(2))
        elif (match := pattern_subproperty.match(line)) is not None:
            parent_property = get_property(match.group(1), match.group(2))
            add_property_inheritance(context_item, parent_property)
        elif (match := pattern_domain.match(line)) is not None:
            add_domain(context_item, match.group(1))
        elif (match := pattern_range.match(line)) is not None:
            add_range(context_item, match.group(1))
        elif (match := pattern_comment.match(line)) is not None:
            add_comment(context_item, match.group(1))

# If there are exclusions, generate the main diagram without the excluded packages.
if len(exclusions) > 0:
    with open(os.path.join(uml_folder, f"ttl_appn-{'-'.join(exclusions)}.txt"), "w") as uml_file:
        uml_file.write("@startuml\n")
        for prefix in packages.keys():
            if prefix not in exclusions:
                if prefix == "appn":
                    for cls in packages[prefix]:
                        uml_file.write(f"class {cls[1]}\n")
                else:
                    uml_file.write (f'package "{prefix}" {{\n')
                    for cls in packages[prefix]:
                        uml_file.write(f"    class {get_name(cls)} {package_colours[prefix]}\n")
                    uml_file.write('}\n')
        for child in inheritance:
            if child[0] not in exclusions:
                for parent in inheritance[child]:
                    if parent[0] not in exclusions:
                        child_name = get_name(child)
                        parent_name = get_name(parent)
                        uml_file.write(f"{child_name} --|> {parent_name}\n")
        uml_file.write("@enduml\n")

# Otherwise generate the standard diagrams and markdown
else:
    # Main diagram with all classes and inheritance.
    with open(os.path.join(uml_folder, f"ttl_appn_full.txt"), "w") as uml_file:
        uml_file.write("@startuml\n")
        for prefix in packages.keys():
            if prefix == "appn":
                for cls in packages[prefix]:
                    uml_file.write(f"class {cls[1]}\n")
            else:
                uml_file.write (f'package "{prefix}" {{\n')
                for cls in packages[prefix]:
                    uml_file.write(f"    class {get_name(cls)} {package_colours[prefix]}\n")
                uml_file.write('}\n')
        for child in inheritance:
            for parent in inheritance[child]:
                if parent[0] not in exclusions:
                    child_name = get_name(child)
                    parent_name = get_name(parent)
                    uml_file.write(f"{child_name} --|> {parent_name}\n")
        uml_file.write("@enduml\n")

    # Class diagrams with inheritance, properties and subclasses
    for appn_class in packages["appn"]:
        cls = appn_class[1]
        with open(os.path.join(uml_folder, f"ttl_appn_{cls}.txt"), "w") as uml_file, \
                open(os.path.join(markdown_folder, f"appn_{cls}.md"), "w") as md_file:
            uri = f"{prefixes['appn']}{cls}"
            md_file.write(f"# {cls}\n")
            md_file.write(f"[{uri}]({uri})\n\n")
            if appn_class in comments:
                md_file.write(f"{comments[appn_class]}\n\n")
            md_file.write(f"![UML diagram for {cls}](/{uml_folder}/ttl_appn_{cls}.png)\n\n")
            uml_file.write("@startuml\n")
            if appn_class in inheritance:
                md_file.write(f"## Superclasses\n")
            write_parents(uml_file, md_file, appn_class, appn_class)
            write_properties(uml_file, md_file, appn_class, appn_class, False)
            write_children(uml_file, md_file, appn_class, appn_class)
            uml_file.write("@enduml\n")

    with open(os.path.join(markdown_folder, "appn_schema.md"), "w") as md_file:
        md_file.write("# APPN Schema Overview\n## APPN Classes\n")
        for appn_class in sorted(packages["appn"]):
            md_file.write(f"* [appn:{appn_class[1]}](/doc/appn_{appn_class[1]}.md)\n")
