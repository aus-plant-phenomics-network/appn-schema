""" 
This code loads ttl files into rdflib as a graph and creates a javascript 
enabled visualisation using pyvis.network

Author : Copilot, with direction from Josh Bowden, APPN
Date: 12/02/2026

Usage: 
python appn_schema_pyvizgraph.py 

then open the html output file: ttl_schema_graph_prefix_colored.html

"""


from rdflib import Graph, RDF, RDFS, OWL, URIRef, Literal
from pyvis.network import Network
from html import escape
from pathlib import Path
import json
import colorsys
import random


from rdflib import Namespace
SCHEMA = Namespace("https://schema.org/")

#  "schemaorg-current-https.ttl" "owl.ttl"  "PPEO.ttl",  "prov.ttl",  "sosa.ttl", "ssn.ttl",  ,  "ddi-cdi.ttl"
TTL_PATH = ["appn-schema.ttl.new"] # <-- change this if needed

dirprefix = './'
# g1 = Graph()
# g1.parse("ddi-cdi.jsonld", format="json-ld")
# g1.serialize(destination="ddi-cdi.ttl", format="turtle") 

g = Graph()
for ttl_path in TTL_PATH:
    print(f'Parsing the input schema : {ttl_path}')
    g.parse(dirprefix+ttl_path, format="turtle")
    
print(f"Loaded triples: {len(g)}")

 
# g.parse(TTL_PATH, format="turtle")
def node_degree_map(g: Graph, ignore_literals=True, undirected=True):
    deg = {}
    for s, p, o in g:
        if not isinstance(s, Literal):
            deg[s] = deg.get(s, 0) + 1
        if not isinstance(o, Literal):
            if undirected:
                deg[o] = deg.get(o, 0) + 1
    return deg

def drop_degree_one_nodes(g: Graph):
    deg = node_degree_map(g)
    to_remove = set(n for n, d in deg.items() if d == 1)
    # Remove any triple that mentions a degree-1 node (subject or object)
    remove_triples = []
    for s, p, o in g:
        if s in to_remove or (o in to_remove and not isinstance(o, Literal)):
            remove_triples.append((s, p, o))
    for t in remove_triples:
        g.remove(t)
    return g


# g = drop_degree_one_nodes(g)
# print(f"Loaded triples: {len(g)}")


def get_classes(g: Graph, include_owl=True):
    classes = set(g.subjects(RDF.type, RDFS.Class))
    if include_owl:
        classes |= set(g.subjects(RDF.type, OWL.Class))
    return classes

def get_all_properties(g: Graph, include_owl=True):
    props = set(g.subjects(RDF.type, RDF.Property))
    if include_owl:
        props |= set(g.subjects(RDF.type, OWL.ObjectProperty))
        props |= set(g.subjects(RDF.type, OWL.DatatypeProperty))
        props |= set(g.subjects(RDF.type, OWL.AnnotationProperty))
    return props

def is_attached_to_class_via_domain_or_range(g: Graph, prop, classes):
    doms = set(g.objects(prop, RDFS.domain))
    rngs = set(g.objects(prop, RDFS.range))
    # A property is "attached" if ANY domain or range is a known class
    return any(d in classes for d in doms) or any(r in classes for r in rngs)

def prune_properties_without_domain_or_range_to_class(g: Graph, include_owl=True):
    classes = get_classes(g, include_owl=include_owl)
    props = get_all_properties(g, include_owl=include_owl)

    to_remove_props = set()
    for p in props:
        if not is_attached_to_class_via_domain_or_range(g, p, classes):
            to_remove_props.add(p)

    # Remove *all* triples where these properties appear as subject or predicate
    remove_triples = []
    for p in to_remove_props:
        # any triples that describe the property node
        for t in g.triples((p, None, None)):
            remove_triples.append(t)
        # any usage of the property as a predicate
        for t in g.triples((None, p, None)):
            remove_triples.append(t)

    for t in remove_triples:
        g.remove(t)
    return g, to_remove_props

# Using these functions to try to prune the graph
# g, removed = prune_properties_without_domain_or_range_to_class(g)
# print(f"Removed {len(removed)} properties; remaining triples: {len(g)}")


# --- collect classes and properties (simplified) ---
classes = set()
properties = set()

for s in g.subjects(RDF.type, RDFS.Class):
    classes.add(s)
for s in g.subjects(RDF.type, OWL.Class):
    classes.add(s)


def label(term):
    lbl = next(g.objects(term, RDFS.label), None)
    return str(lbl) if lbl else None

for s in sorted(set(g.subjects()), key=str):
    types = list(g.objects(s, RDF.type))
    # print(f"{s}    [{label(s) or ''}]    --> {types}")


for s in g.subjects(RDF.type, RDF.Property):
    properties.add(s)
for s in g.subjects(RDF.type, OWL.ObjectProperty):
    properties.add(s)
for s in g.subjects(RDF.type, OWL.DatatypeProperty):
    properties.add(s)
for s in g.subjects(RDF.type, OWL.AnnotationProperty):
    properties.add(s)
# print("classes:")
# print(*classes, sep="\n") 
# print("-- no more classes")
# print("properties:")
# print(*properties, sep="\n")
# print("-- no more properties")
# ---------- helpers: label, comment, prefix, colors ----------

# classes = drop_degree_one_nodes(classes)
# print(f"Loaded triples: {len(g)}")

DEFAULT_IGNORE = {"rdf", "rdfs", "xsd", "owl", "<https"}

def prefixes_used_in_graph(g: Graph, ignore=DEFAULT_IGNORE):
    """
    Return a set of prefixes used in predicate/object positions in the graph,
    excluding subject prefixes and any in `ignore`.
    """
    used = set()

    # Collect prefixes from predicate and object positions
    for s, p, o in g:
        # Predicates are always URIs in RDF triples
        curie_p = g.namespace_manager.normalizeUri(p)  # e.g., 'rdfs:subClassOf' or a full IRI if no prefix
        if ":" in curie_p:
            pfx = curie_p.split(":", 1)[0]
            if pfx not in ignore:
                used.add(pfx)

        # Object may be a URI or not (Literal/BlankNode)
        if isinstance(o, URIRef):
            curie_o = g.namespace_manager.normalizeUri(o)
            if ":" in curie_o:
                pfx = curie_o.split(":", 1)[0]
                if pfx not in ignore:
                    used.add(pfx)

    # Remove subject prefixes
    for s, _, _ in g:
        if isinstance(s, URIRef):
            curie_s = g.namespace_manager.normalizeUri(s)
            if ":" in curie_s:
                used.discard(curie_s.split(":", 1)[0])

    return used


from urllib.parse import urlparse

def to_appn_github_uri(uri: str,
                       expected_host: str = "schema.plantphenomics.org.au",
                      # redirect_url: str = "https://github.com/aus-plant-phenomics-network/appn-schema/"
                      # "blob/main/doc/",
                      redirect_url: str = "https://aus-plant-phenomics-network.github.io/appn-schema/",
        
                       require_https: bool = False,
                       add_md: bool = False ) -> str:
    """
    Convert an APPN schema term URI like
      https://schema.plantphenomics.org.au/Variable
    to the GitHub docs URL:
      https://github.com/aus-plant-phenomics-network/appn-schema/blob/main/doc/appn_Variable.md

    Validates that the URI points to the expected host (and https if required).

    Parameters
    ----------
    uri : str
        The input IRI/URL string for an APPN term.
    expected_host : str
        Hostname to validate (default: 'schema.plantphenomics.org.au').
    require_https : bool
        If True, enforce https scheme.

    Returns
    -------
    str
        The GitHub documentation URL.

    Raises
    ------
    ValueError 
        If the URL is invalid, host/scheme doesn’t match, or name part is missing.
    """
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("URI must be a non-empty string")

    p = urlparse(uri)

    # Basic scheme/host validation
    if require_https and p.scheme.lower() != "https":
        raise ValueError(f"Expected https scheme, got: {p.scheme!r}")
    if p.netloc.lower() != expected_host.lower():
        raise ValueError(f"Expected host {expected_host!r}, got: {p.netloc!r}")

    # Extract the 'local name' from the path:
    # e.g., '/Variable' -> 'Variable'
    # If someone passes a trailing slash, handle it.
    path = p.path or ""
    local = path.rstrip("/").split("/")[-1] if path else ""
    if not local:
        raise ValueError(f"Could not extract local name from path: {path!r}")
    
    if add_md :
        # Form the GitHub docs filename pattern: appn_<Local>.md
        filename = f"appn_{local}.md"
    else: 
        filename = f"appn_{local}/"

    # Build the final GitHub URL
    gh_url = (
        redirect_url + filename
    )
    return gh_url

def best_label(term):
    """Prefer rdfs:label; otherwise compact IRI tail."""
    lbl = next(g.objects(term, RDFS.label), None)
    if isinstance(lbl, Literal):
        return str(lbl)
    s = str(term)
    for sep in ("#", "/"):
        if sep in s:
            s = s.rsplit(sep, 1)[-1]
    return s

def best_comment(term, lang_pref=("en", None)):
    """
    Tooltip string from rdfs:comment (language-pref aware).
    lang_pref: tuple of preferred languages; None means 'no lang tag'.
    """
    comments = list(g.objects(term, RDFS.comment))
    if not comments:
        return None
    # language preference
    for lang in lang_pref:
        for c in comments:
            if isinstance(c, Literal):
                if (lang is None and c.language is None) or (
                    lang and c.language and c.language.lower().startswith(lang)
                ):
                    return str(c)
    # fallback: join them (shortened)
    joined = " \n".join(str(c) for c in comments if isinstance(c, Literal))
    if len(joined) > 500:
        joined = joined[:500] + "…"
    return joined or None

def qname_prefix(term: URIRef) -> str:
    """
    Return the rdflib prefix for a term, e.g., 'schema', 'rdf', 'owl'.
    Falls back to '' if no prefix can be computed.
    """
    try:
        qn = g.compute_qname(term)  # returns (prefix, namespace, localname)
        return qn[0] or ""
    except Exception:
        return ""

def qname_local(term: URIRef) -> str:
    try:
        qn = g.compute_qname(term)
        return qn[2]
    except Exception:
        return best_label(term)

# Build the set of prefixes actually used by our terms
all_terms = list(classes) + list(properties)
prefixes_used = []
prefix_set = set()
# for t in all_terms:
    # if isinstance(t, URIRef):
        # px = qname_prefix(t)
        # if px not in prefix_set:
            # prefix_set.add(px)
            # prefixes_used.append(px)
            
# print(*all_terms, sep="\n")
# This works well:
prefixes_used = prefixes_used_in_graph(g)
print("prefixes_used:")
print(prefixes_used)

# Choose a distinct color per prefix.
# We'll generate HSL hues for variety and then map to hex.
def hsl_to_hex(h, s, l):
    r, g_, b = colorsys.hls_to_rgb(h, l, s)
    return f"#{int(r*255):02x}{int(g_*255):02x}{int(b*255):02x}"

random.seed(42)  # stable colors across runs
palette = []
# Distribute hues around the color wheel
for i in range(max(6, len(prefixes_used))):
    h = (i / max(6, len(prefixes_used))) % 1.0
    # pleasant saturation/lightness
    s = 0.55
    l = 0.58
    # small jitter to improve contrast when many prefixes exist
    h += random.uniform(-0.02, 0.02)
    h = (h + 1.0) % 1.0
    palette.append(hsl_to_hex(h, s, l))

prefix_to_color = {
    "appn":   "#5E81AC",
    "schema": "#E76F51",
    "sosa":   "#2A9D8F",
    "ssn":    "#1D3557",
    "prov":   "#6A4C93",
    "ppeo":   "#8ECAE6",
    "bio":    "#4E9F3D",
    "cdi":    "#F4A261",
    "owl":    "#9B2226",
    "rdf":    "#2B2D42",
    "rdfs":   "#6C757D",
}
fallback_color = "#888888"
for i, px in enumerate(prefixes_used):
    prefix_to_color[px] = palette[i % len(palette)]

# For terms without a detectable prefix, keep a neutral color
prefix_to_color[""] = fallback_color

import re

def linebreak_after_sentences(text: str) -> str:
    """
    Insert a newline after each sentence in `text`, except the last sentence.

    Heuristic:
    - A sentence ends with ., ?, or !, optionally followed by a closing quote/paren/bracket.
    - Only add a newline if that is followed by whitespace and then a capital letter or a digit.
      This helps avoid splitting after abbreviations like "e.g." or "Dr." when lowercase follows.

    Examples:
        "Hello world. This is fine! Right?" ->
            "Hello world.\nThis is fine!\nRight?"

        'He met Dr. Smith. They talked at 10 a.m. It was useful.' ->
            'He met Dr. Smith.\nThey talked at 10 a.m.\nIt was useful.'
    """
    if not text:
        return text

    # Capture the sentence-ending chunk, then replace the following whitespace with a newline
    # ONLY when the next token starts with [A-Z0-9].
    pattern = r'([.!?]["\')\]]?)\s+(?=[A-Z0-9])'
    return re.sub(pattern, r'\1\n', text.strip())


def node_style_for_term(term: URIRef, is_property: bool):
    px = qname_prefix(term)
    color = prefix_to_color.get(px, fallback_color)
    shape = "diamond" if is_property else "dot"
    return color, shape, px

def make_node_label(term: URIRef, is_property: bool):
    """
    Show 'prefix:LocalName' prominently. If there is a distinct rdfs:label,
    append it on a second line (smaller in tooltip).
    """
    px = qname_prefix(term)
    local = qname_local(term)
    core = f"{px}:{local}" if px else local
    return core


def make_node_title(term: URIRef, px: str):
    """
    Tooltip: bold prefix:local, full IRI, and rdfs:comment (if any).
    HTML is allowed in 'title' for PyVis.
    """
    local = qname_local(term)
    display = f"{px}:{local}" if px else local
    iri = escape(str(term))
    comment = best_comment(term)
    comment = linebreak_after_sentences(comment)
    c_html = ""
    if comment:
        c_html = f"""{escape(display)}
        {iri}
          {(comment or '')}
        """
    else:
        c_html = f"""{escape(display)}
        {iri}"""
    return c_html

def make_node_uri(term: URIRef):
    iri = escape(str(term))
    return iri
    
# ---------- build network ----------
net = Network(height="1020px", width="100%", directed=True)
net.toggle_physics(True)

# Add nodes for classes and properties with prefix-based coloring
def add_node(net, n, is_property: bool):
    nid = str(n)
    if nid in net.node_ids:
        return
    color, shape, px = node_style_for_term(n, is_property)
    label = make_node_label(n, is_property)
    title = make_node_title(n, px)
    
    uri   = make_node_uri(n)
    try:
        uri = to_appn_github_uri(uri)
    except ValueError as e:
        None 
        #print(f'No issue with uri rewrite: {e}')
        
    net.add_node(
        nid,
        label=label,
        title=title,   # hover tooltip
        color=color,
        shape=shape,
        font={"face": "Inter", "size": 18},
        url=uri,
    )

for c in classes:
    add_node(net, c, is_property=False)

for p in properties:
    add_node(net, p, is_property=True)

# Edges: subClassOf, domain, range (keep your original colors)
for c in classes:
    for parent in g.objects(c, RDFS.subClassOf):
        if isinstance(parent, URIRef):
            add_node(net, parent, is_property=False)
            net.add_edge(str(c), str(parent), label="subClassOf", color="#4c566a")

for p in properties:
    for d in g.objects(p, SCHEMA.domainIncludes):
        if isinstance(d, URIRef):
            add_node(net, d, is_property=False)
            net.add_edge(str(p), str(d), label="domainIncludes", color="#a3be8c")
    for r in g.objects(p, SCHEMA.rangeIncludes):
        if isinstance(r, URIRef):
            add_node(net, r, is_property=False)
            net.add_edge(str(p), str(r), label="rangeIncludes", color="#bf616a")
    for s in g.objects(p, RDFS.subPropertyOf):
        if isinstance(s, URIRef):
            add_node(net, s, is_property=False)
            net.add_edge(str(p), str(s), label="subPropertyOf", color="#bf916a")


# ---------- legend (prefix → color) ----------
# We'll pin legend nodes at the top-left and disable physics for them.
legend_group = "Legend"
legend_nodes = []
x0, y0 = -1300, -1300
dx, dy = 0, 60

# Only list prefixes that actually appear (preserves compactness)
legend_items = [(px if px else "(no prefix)", prefix_to_color[px]) for px in prefixes_used or [""]]

for i, (px, col) in enumerate(legend_items):
    node_id = f"legend::{i}"
    net.add_node(
        node_id,
        label=str(px),
        title=f"prefix: {px}",
        color=col,
        shape="box",
        physics=False,
        fixed=True,
        x=x0 + dx,
        y=y0 + i * dy,
        font={"face": "Inter", "size": 24},
    )
    legend_nodes.append(node_id)

# 
dx, dy = 0, 60
i = i + 1
node_id = f"legend::{i}"
net.add_node(
    node_id,
    label='Class',
    title=f"Denotes an rdf:Class",
    color={
        "border": "#000000",
        "background": "rgba(0,0,0,0)",            # transparent fill
        "highlight": { "border": "#000000", "background": "rgba(0,0,0,0)" },
        "hover":     { "border": "#000000", "background": "rgba(0,0,0,0)" },
    },
    borderWidth=1,
    shape="circle",
    physics=False,
    fixed=True,
    x=x0 + dx,
    y=y0 + i * dy,
    font={"face": "Inter", "size": 20},
)
legend_nodes.append(node_id)
i = i + 1
node_id = f"legend::{i}"
net.add_node(
    node_id,
    label='Property',
    title=f"Denotes an rdf:Property",
    color={
        "border": "#000000",
        "background": "rgba(0,0,0,0)",            # transparent fill
        "highlight": { "border": "#000000", "background": "rgba(0,0,0,0)" },
        "hover":     { "border": "#000000", "background": "rgba(0,0,0,0)" },
    },
    borderWidth=1,
    shape="diamond",
    physics=False,
    fixed=True,
    x=x0 + dx,
    y=y0 + i * dy,
    font={"face": "Inter", "size": 20},
)
legend_nodes.append(node_id)


rangeIncDef = 'rangeIncludes: The value of the property is typically of these types.'
domainIncDef ='domainIncludes: The property is typically used on instances of these classes.' 
# Small header for the legend
net.add_node(
    "legend::header",
    label=f"Legend (prefix → color)\n{rangeIncDef}\n{domainIncDef}",
    color="#222222",
    shape="box",
    physics=False,
    fixed=True,
    x=x0 - 20,
    y=y0 - 80,
    font={"face": "Inter", "size": 26, "bold": True, "color": "#ffffff", "align": "left"},
)

# ---------- vis.js options ----------
opts = { 
    "edges": { "arrows": "to", "smooth": {"type": "dynamic"} },
    "nodes": { "font": { "face": "Inter", "size": 16 } },
    "physics": {
        "enabled": True,
        "solver": "forceAtlas2Based",
        "forceAtlas2Based": { "gravitationalConstant": -50 },
        "damping": 0.60,        # ↑ makes motion more sluggish (0..1)
        "minVelocity": 0.5,     # stops tiny jitter sooner
        "maxVelocity": 5,       # caps speed (default is higher)
        "timestep": 0.3,        # smaller step = calmer updates
        "stabilization": { "enabled": True, "iterations": 100 }
    }
}
net.set_options(json.dumps(opts))

# ---------- write HTML ----------
out_path = "appn-schema-pyviz.html"
net.write_html(out_path, open_browser=False)
print(f"Wrote {out_path}")


# Inject a click handler that opens node.url in a new tab
html = Path(out_path).read_text(encoding="utf-8")

injection = """
// Open node.url in a new tab when a node is clicked
network.on("doubleClick", function (params) {
  if (params.nodes && params.nodes.length > 0) {
    var nodeId = params.nodes[0];
    try {
      var node = nodes.get(nodeId);
      if (node && node.url) {
        window.open(node.url, "_blank", "noopener,noreferrer");
      }
    } catch (e) {
      console.error("Could not open node URL:", e);
    }
  }
});
"""

# Heuristic: insert right after the network is instantiated.
# We look for the line that creates 'network = new vis.Network(...);'
marker = "var network = new vis.Network(container, data, options);"
if marker in html:
    html = html.replace(marker, marker + "\n" + injection)
else:
    # Fallback: append near the end before </script>
    html = html.replace("</script>", injection + "\n</script>")

Path(out_path).write_text(html, encoding="utf-8")
print(f"Injected node-click URL handler into {out_path}")
