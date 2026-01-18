"""
The morsegraph package constructs a trie (prefix tree) from a static
list of International Morse code sequences (ITU M.1677). It generates a
hierarchical representation of the data and exports it as a JSON structure
and several visual formats (PDF, PNG, SVG) using Graphviz.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any, Dict

import pydot

# A marker used to signify that a specific node represents the completion
# of a full sequence in the trie.
END = "_end"

# Type alias: A dictionary where keys are single characters (dots, dashes, or
# letters) and values are nested dictionaries, except for the END key.
TrieNode = Dict[str, Any]

# MORSE_DATA follows the International Morse code mapping from ITU M.1677.
# Note: Each string contains the dot/dash sequence followed by the character.
# Example: ".-A" means the path '.' -> '-' leads to the leaf 'A'.
MORSE_DATA = [
    # fmt: off
    ".-A", "-...B", "-.-.C", "-..D", ".E", "..-.F", "--.G", "....H", "..I",
    ".---J", "-.-K", ".-..L", "--M", "-.N", "---O", ".--.P", "--.-Q", ".-.R",
    "...S", "-T", "..-U", "...-V", ".--W", "-..-X", "-.--Y", "--..Z", "-----0",
    ".----1", "..---2", "...--3", "....-4", ".....5", "-....6", "--...7",
    "---..8", "----.9", ".-.-.-.", "--..--,", "---...:", "..--..?", ".----.’",
    "-....-–", "-..-./", "-.--.(", "-.--.-)", '.-..-."', "-...-=", ".-.-.+",
    ".--.-.@",
    # fmt: on
]


def _new_node() -> TrieNode:
    """Initializes a new trie node with a terminal marker set to False."""
    return {END: False}


def _insert_word(root: TrieNode, word: str) -> None:
    """
    Traverses the trie and inserts each character of the word as a node.

    Args:
        root: The starting node of the trie.
        word: The string sequence (e.g., '.-A') to insert.
    """
    node = root
    for ch in word:
        # Move to existing child node or create a new one if it doesn't exist
        node = node.setdefault(ch, _new_node())
    # Mark the final node as a terminal node
    node[END] = True


def _build_trie_from_static() -> TrieNode:
    """Iterates through MORSE_DATA to populate the trie structure."""
    root = _new_node()
    for entry in MORSE_DATA:
        if entry:
            _insert_word(root, entry)
    return root


def _trie_to_pydot(
    trie: TrieNode, *, rankdir: str = "TB"
) -> pydot.Dot:
    """
    Transforms the trie dictionary into a Graphviz/pydot visualization.

    Args:
        trie: The root node of the trie.
        rankdir: The orientation of the resulting graph.

    Returns:
        A pydot.Dot object ready for rendering.
    """
    graph = pydot.Dot(graph_type="digraph", rankdir=rankdir)

    graph.set(
        name="label",
        value="INTERNATIONAL MORSE CODE TRIE - "
        + "github.com/pierow2k/morsegraph",
    )
    graph.set(
        name="URL", value="https://github.com/pierow2k/morsegraph"
    )
    graph.set(name="labelloc", value="b")
    graph.set(name="fontsize", value="24")
    graph.set(name="labeljust", value="r")

    # Counter to ensure every node in the graph has a unique ID
    node_index = itertools.count(0)

    def _add_node(
        *, label: str, terminal: bool = False, root: bool = False
    ) -> tuple[str, int]:
        """Helper to create a stylized pydot Node."""
        idx = next(node_index)
        node_name = f"n{idx}"
        attrs = {"label": label}

        if root:
            # Root node is a simple box
            attrs["shape"] = "box"
        elif terminal:
            # Terminal nodes (leaf characters) are highlighted in green
            attrs["shape"] = "doublecircle"
            attrs["fillcolor"] = "#007F01"
            attrs["fontcolor"] = "white"
            attrs["style"] = "filled"
        else:
            # Intermediate nodes (dots and dashes) use different grays
            attrs["shape"] = "circle"
            attrs["fontname"] = "Courier-Bold"
            attrs["fontsize"] = "18"
            attrs["fontcolor"] = "white"
            attrs.update(
                {"style": "filled", "fillcolor": "#3b3b3b"}
                if label != "."
                else {"style": "filled", "fillcolor": "#808080"}
            )

        graph.add_node(
            pydot.Node(name=node_name, obj_dict=None, **attrs)
        )
        return node_name, idx

    def _walk(node: TrieNode, parent_name: str) -> None:
        """Recursively traverses the trie dictionary to add edges to
        the graph."""
        for ch, child in node.items():
            # Skip the metadata key; only process actual character branches
            if ch == END or not isinstance(child, dict):
                continue

            child_name, _ = _add_node(
                label=ch,
                terminal=bool(child.get(END, False)),
            )
            # Edge labels show the node order/index for debugging
            graph.add_edge(pydot.Edge(parent_name, child_name))
            _walk(child, child_name)

    # Initialize the recursive walk starting from the root
    root_name, _ = _add_node(
        label="root", terminal=bool(trie.get(END, False)), root=True
    )
    _walk(trie, root_name)

    # TODO: Add a centered title at the top
    # graph.attr(label='My Graph Title', labelloc='t', fontsize='20')

    return graph


def _write_json_output(json_filepath: Path, trie: TrieNode) -> None:
    """Serializes the trie structure to a JSON file for programmatic use."""
    json_filepath.parent.mkdir(parents=True, exist_ok=True)
    with json_filepath.open(
        "w", encoding="utf-8", newline="\n"
    ) as fp:
        json.dump(trie, fp, indent=2, ensure_ascii=False)


def _write_graphviz_outputs(graph: pydot.Dot, basename: Path) -> None:
    """Renders the pydot graph into multiple file formats."""
    basename.parent.mkdir(parents=True, exist_ok=True)

    for fmt in ("gv", "pdf", "png", "svg"):
        path = basename.with_suffix(f".{fmt}")
        # graph.write handles calling the underlying Graphviz 'dot' command
        graph.write(str(path), format=fmt)


def make_graphs(
    basename: Path, directory: Path, rankdir: str
) -> None:
    """
    Orchestrates the building, data saving, and rendering of the trie.

    Args:
        basename: The base filename for generated outputs.
        directory: The directory for generated outputs.
        rankdir: The orientation of the resulting graph.
    """

    basename = directory / basename

    # Build logic representation
    trie = _build_trie_from_static()

    # Save raw data in JSON format
    _write_json_output(basename.with_suffix(".json"), trie)

    # Create visual representation
    graph = _trie_to_pydot(trie, rankdir=rankdir)

    # Export images and Graphviz dot files
    _write_graphviz_outputs(graph, basename=basename)


if __name__ == "__main__":
    pass
