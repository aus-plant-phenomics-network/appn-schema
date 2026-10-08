from rdflib import Graph
import sys

if len(sys.argv) > 1:
    g = Graph()
    for asset in sys.argv[1:]:
        g.parse(asset)

    nm = g.namespace_manager
    nm.bind("appn", "https://schema.plantphenomics.org.au/")
    for s, p, o in g:
        print(f"{repr(s)} ({type(s)})\n    {repr(p)} ({type(p)})\n        {repr(o)} ({type(o)})")
        #print(f"{repr(nm.normalizeUri(s))}\n    {repr(nm.normalizeUri(p))}\n        {repr(o)}")
    #print(g.serialize(format="n3"))