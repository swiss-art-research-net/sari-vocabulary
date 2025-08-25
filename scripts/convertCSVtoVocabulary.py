import argparse, csv
from rdflib import Graph, Literal, Namespace, URIRef, Literal
from rdflib.namespace import RDF, SKOS, DCTERMS

def convertCSVtoVocabulary(inputFile, outputFile, namespace, schemeURI=None, schemeLabel=None, lang="en"):
    namespaceString = sanitiseNamespace(namespace)
    NS = Namespace(namespaceString)
    schemeURI = URIRef(schemeURI) if schemeURI else URIRef(namespaceString.rstrip("#/"))

    g = Graph()
    g.bind("skos", SKOS)
    g.bind("dcterms", DCTERMS)
    g.bind("vocab", NS)

    g.add((schemeURI, RDF.type, SKOS.ConceptScheme))
    if schemeLabel:
        g.add(schemeURI, SKOS.prefLabel, Literal(schemeLabel, lang=lang))

    rows = []
    with open(inputFile, newline="", encoding="utf-8") as f:
        r = csv.DictReader(f)
        r.fieldNames = [h.strip() for h in r.fieldnames] if r.fieldnames else r.fieldnames
        for row in r:
            # Strip field
            f = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
            rows.append(f)
    
    concepts = {}
    
    # Create Concepts
    for row in rows:
        conceptID = row.get("ID") or row.get("id")
        if not conceptID:
            continue
        uri = URIRef(namespaceString + conceptID)
        concepts[conceptID] = uri
        g.add((uri, RDF.type, SKOS.Concept))
        g.add((uri, SKOS.inScheme, schemeURI))

        # prefLabel
        prefLabel = row.get("prefLabel") or row.get("preflabel")
        if prefLabel:
            g.add((uri, SKOS.prefLabel, Literal(prefLabel, lang=lang)))

        # altLabel(s)
        altLabels = row.get("altLabel") or row.get("altlabel")
        if altLabels:
            for altLabel in altLabels.split(","):
                g.add((uri, SKOS.altLabel, Literal(altLabel.strip(), lang=lang)))
        
        # definition
        definition = row.get("definition") or row.get("Definition")
        if definition:
            g.add((uri, SKOS.definition, Literal(definition, lang=lang)))

        
        # example
        example = row.get("example") or row.get("Example")
        if example:
            g.add((uri, SKOS.example, Literal(example, lang=lang)))

        # exactMatch
        exactMatch = row.get("exactMatch") or row.get("ExactMatch")
        if exactMatch:
            g.add((uri, SKOS.exactMatch, Literal(exactMatch, lang=lang)))

        # closeMatch
        closeMatch = row.get("closeMatch") or row.get("CloseMatch")
        if closeMatch:
            g.add((uri, SKOS.closeMatch, Literal(closeMatch, lang=lang)))

    # Link Concepts
    hasBroader =  set()
    for row in rows:
        conceptID = row.get("ID") or row.get("id")
        if not conceptID or conceptID not in concepts:
            continue
        broaderValues = splitMulti(row.get("broader") or "")
        for broader in broaderValues:
            if broader in concepts:
                g.add((concepts[conceptID], SKOS.broader, concepts[broader]))
                g.add((concepts[broader], SKOS.narrower, concepts[conceptID]))
                hasBroader.add(conceptID)

    # Top concepts
    for conceptID, uri in concepts.items():
        if conceptID not in hasBroader:
            g.add((schemeURI, SKOS.hasTopConcept, uri))
            g.add((uri, SKOS.topConceptOf, schemeURI))

    data = g.serialize(format="turtle")
    with open(outputFile, "w") as f:
        f.write(data)

def sanitiseNamespace(ns: str) -> str:
    return ns if ns.endswith(("#", "/")) else ns + "#"

def splitMulti(s):
    if not s:
        return []
    # support | or ; as multi-value separators
    return [x.strip() for x in s.replace(";", "|").split("|") if x.strip()]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert CSV to RDF")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output TTL file")
    parser.add_argument("--namespace", required=True, help="Namespace for concept URIs (e.g., https://example.org/vocab#)")
    parser.add_argument("--scheme-uri", help="URI for the ConceptScheme (default: namespace without trailing #/)")
    parser.add_argument("--scheme-label", help="Human label for the ConceptScheme")
    parser.add_argument("--lang", default="en", help="Language tag for labels/notes (default: en)")

    args = parser.parse_args()
    convertCSVtoVocabulary(
        inputFile=args.input,
        outputFile=args.output,
        namespace=args.namespace,
        schemeURI=args.scheme_uri,
        schemeLabel=args.scheme_label,
        lang=args.lang
    )