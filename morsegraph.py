#!/usr/bin/env python
"""
morsegraphy.py - Morse Code Trie Visualizer CLI

This script constructs a trie (prefix tree) from a static list of International
Morse code sequences (ITU M.1677). It generates a hierarchical representation
of the data and exports it as a JSON structure and several visual formats
(PDF, PNG, SVG) using Graphviz. It uses the `morsegraph` package to generate
its output.

Usage:
    python morsegraphy.py
"""

import argparse
from pathlib import Path
import morsegraph

__version__ = "1.0.0"


def _parse_args() -> argparse.Namespace:
    """Parses command-line arguments for output customization."""
    p = argparse.ArgumentParser(
        description="Builds and creates visualizations of a trie for "
        "International Morse code based on ITU M.1677."
    )
    p.add_argument(
        "--basename",
        default="morsegraph",
        type=Path,
        help="The base filename for generated outputs (default: morsegraph).",
    )
    p.add_argument(
        "--dir",
        default="./output",
        type=Path,
        help="The directory for generated outputs (default: ./output).",
    )
    p.add_argument(
        "--rankdir",
        default="TB",
        choices=["TB", "BT", "LR", "RL"],
        help="The direction of the graph: TB (Top-to-Bottom), "
        "LR (Left-to-Right).",
    )
    p.add_argument(
        "--version",
        "-v",
        action="version",
        version="%(prog)s v" + __version__,
    )

    return p.parse_args()


def main() -> None:
    """Parses arguments and calls morsegraph to build and render the trie."""
    args = _parse_args()

    morsegraph.make_graphs(
        basename=args.basename,
        directory=args.dir,
        rankdir=args.rankdir,
    )

    print(f"Visualizations saved to '{args.dir}'")


if __name__ == "__main__":
    main()
