import re
from collections import defaultdict, OrderedDict, deque
from rdflib import Graph, Namespace, RDF, RDFS, OWL

OWL_FILE_PATH = "data/TestProfile.owl"  # Update to your OWL file
CSHARP_OUTPUT_FILE = "GeneratedClasses.cs"

XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Basic XSD-to-C# type map (extend as needed)
XSD_TO_CSHARP = {
    str(XSD.string): "string",
    str(XSD.boolean): "bool",
    str(XSD.float): "float",
    str(XSD.double): "double",
}

def shorten_uri(uri):
    """Extracts the local name from a URI (or returns empty if none)."""
    if not uri:
        return ""
    return re.split(r"[#/]", str(uri))[-1]

def is_named_class_local_name(local_name: str) -> bool:
    """
    Decide if 'local_name' is a meaningful class name rather than an ephemeral blank node.
    Skip local names that match ^N[0-9a-fA-F]{8,}.
    """
    if not local_name:
        return False
    if re.match(r"^N[0-9a-fA-F]{8,}", local_name):
        # Looks like an auto-generated blank node
        return False
    return True

def make_csharp_identifier(raw_name: str) -> str:
    """Converts a name to a valid C# identifier, capitalizing the first letter."""
    if "." in raw_name:
        raw_name = raw_name.split(".")[-1]
    if not raw_name:
        return raw_name
    return raw_name[0].upper() + raw_name[1:]

class OwlClassInfo:
    """Container for a single OWL class's data."""
    def __init__(self, uri, name):
        self.uri = uri
        self.name = name
        self.parent_name = None
        self.data_properties = OrderedDict()
        self.object_properties = OrderedDict()

def parse_owl(owl_path):
    """Main parsing function: build a dictionary of real named classes."""
    g = Graph()
    g.parse(owl_path, format="xml")

    # Step 1: gather all classes
    all_class_uris = set(g.subjects(RDF.type, OWL.Class))

    # Step 2: keep only named classes (skip ephemeral)
    classes = {}
    for cls_uri in all_class_uris:
        local_name = shorten_uri(cls_uri)
        if is_named_class_local_name(local_name):
            classes[local_name] = OwlClassInfo(cls_uri, local_name)

    # Step 3: subClassOf adjacency
    subclass_map = defaultdict(list)
    for cls_name, info in classes.items():
        for superclass in g.objects(subject=info.uri, predicate=RDFS.subClassOf):
            subclass_map[cls_name].append(superclass)

    # Step 4: pick a single parent if possible
    for cls_name, super_list in subclass_map.items():
        for candidate in super_list:
            if (candidate, RDF.type, OWL.Restriction) in g:
                continue
            parent_local = shorten_uri(candidate)
            if parent_local in classes and parent_local != cls_name:
                classes[cls_name].parent_name = parent_local
                break

    # Step 5: gather property restrictions
    for cls_name, cls_info in classes.items():
        for superclass_node in g.objects(subject=cls_info.uri, predicate=RDFS.subClassOf):
            if (superclass_node, RDF.type, OWL.Restriction) not in g:
                continue
            prop = g.value(superclass_node, OWL.onProperty)
            all_values = g.value(superclass_node, OWL.allValuesFrom)
            if prop and all_values:
                prop_name = make_csharp_identifier(shorten_uri(prop))
                csharp_type = guess_csharp_type(g, all_values, classes)
                # Decide data vs object property
                if csharp_type in ["string","bool","int","float","double","object"]:
                    cls_info.data_properties.setdefault(prop_name, csharp_type)
                else:
                    cls_info.object_properties.setdefault(prop_name, csharp_type)

    # Step 6: push up inherited properties
    stabilized = False
    while not stabilized:
        stabilized = True
        for cls_info in classes.values():
            if cls_info.parent_name and cls_info.parent_name in classes:
                parent = classes[cls_info.parent_name]
                for p in list(cls_info.data_properties.keys()):
                    if p in parent.data_properties:
                        del cls_info.data_properties[p]
                        stabilized = False
                for p in list(cls_info.object_properties.keys()):
                    if p in parent.object_properties:
                        del cls_info.object_properties[p]
                        stabilized = False

    return classes, g

def guess_csharp_type(g, restriction_target, classes):
    """
    Determine the C# type for 'restriction_target':
      1) If direct match in XSD_TO_CSHARP => returns e.g. 'string', 'bool'.
      2) If 'owl:equivalentClass' is an XSD type => use that.
      3) If local_name is a recognized named class => use that.
      4) If local_name is ephemeral => BFS up via subClassOf or unionOf to find a named class.
      5) If we find exactly 1 named class => use it. Otherwise => 'object'.
    """
    # Step A: direct XSD
    if str(restriction_target) in XSD_TO_CSHARP:
        return XSD_TO_CSHARP[str(restriction_target)]

    # Step B: owl:equivalentClass => XSD
    eq_class = g.value(restriction_target, OWL.equivalentClass)
    if eq_class and str(eq_class) in XSD_TO_CSHARP:
        return XSD_TO_CSHARP[str(eq_class)]

    # Step C: If it's a recognized named class
    local_name = shorten_uri(restriction_target)
    if local_name in classes:
        return local_name

    # Step D: BFS or DFS to find a named class
    found = find_named_class(restriction_target, g, classes)
    if found is not None:
        return found

    # Step E: fallback to 'object'
    return "object"

def find_named_class(start_node, graph, classes):
    """
    Attempt BFS up 'rdfs:subClassOf' and 'owl:unionOf' to see if
    we can find exactly ONE recognized named class among the ancestors.
    If none or more than one => return None.
    """
    visited = set()
    queue = deque([start_node])
    found_named = set()

    while queue:
        current = queue.popleft()
        if current in visited:
            continue
        visited.add(current)

        # If the local name is recognized, record it
        loc_name = shorten_uri(current)
        if loc_name in classes:
            found_named.add(loc_name)

        # subClassOf edges
        for sup in graph.objects(current, RDFS.subClassOf):
            queue.append(sup)

        # unionOf => e.g. <owl:unionOf rdf:nodeID="x123"/>
        union_node = graph.value(current, OWL.unionOf)
        if union_node:
            # union_node is typically an rdf:List => BFS all items in the list
            items = list_of_union_members(graph, union_node)
            for i in items:
                queue.append(i)

    # If exactly 1 unique named class is found, use it
    if len(found_named) == 1:
        return found_named.pop()
    else:
        return None

def list_of_union_members(graph, list_node):
    """
    Recursively gather rdf:first/rdf:rest items from an RDF list (for unionOf).
    Returns a list of items in the union.
    """
    items = []
    current = list_node
    while current and current != RDF.nil:
        first = graph.value(current, RDF.first)
        rest = graph.value(current, RDF.rest)
        if first:
            items.append(first)
        current = rest
    return items

def generate_csharp_code(classes):
    """Generate final C# code from the class dictionary."""
    # Sort by inheritance depth
    def depth(c):
        d = 0
        parent = classes[c].parent_name
        while parent in classes:
            d += 1
            parent = classes[parent].parent_name
        return d

    sorted_classes = sorted(classes.keys(), key=depth)

    lines = []
    lines.append("// Auto-generated from OWL (with BFS resolution) using rdflib in Python")
    lines.append("namespace CIMProfile\n{")

    for cls_name in sorted_classes:
        info = classes[cls_name]
        parent_decl = ""
        if info.parent_name and info.parent_name in classes:
            parent_decl = f" : {info.parent_name}"

        lines.append(f"    public class {cls_name}{parent_decl}")
        lines.append("    {")
        for prop_name, prop_type in info.data_properties.items():
            lines.append(f"        public {prop_type} {prop_name} {{ get; set; }}")
        for prop_name, prop_type in info.object_properties.items():
            lines.append(f"        public {prop_type} {prop_name} {{ get; set; }}")
        lines.append("    }\n")

    lines.append("}")
    return "\n".join(lines)

def main():
    classes, graph = parse_owl(OWL_FILE_PATH)
    csharp_code = generate_csharp_code(classes)
    with open(CSHARP_OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(csharp_code)
    print(f"[INFO] Wrote C# classes to:", CSHARP_OUTPUT_FILE)

if __name__ == "__main__":
    main()
