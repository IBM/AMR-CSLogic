"""
Module to deal with reification of AMR parse.
"""
import csv
from typing import Optional, Dict, Set, List, Tuple
import logging

from penman.types import (Variable, Target, BasicTriple, Node)
from penman.exceptions import ModelError
from penman.epigraph import (Epidatum, Epidata)
from penman.surface import (Alignment, RoleAlignment, alignments)
from penman.tree import (Tree, is_atomic)
from penman.graph import (Graph, CONCEPT_ROLE)
from penman.model import Model
from penman.layout import (
    Push,
    Pop,
    POP,
    appears_inverted,
    get_pushed_variable,
)

from penman.codec import PENMANCodec
from penman.models.amr import model
from penman.transform import _SplitMarkers, _reified_markers, _edge_markers

logger = logging.getLogger(__name__)

MAPPING_FILE_PATH = "data/reification/mappings.tsv"


def read_mappings(path):
    with open(path) as file:
        tsv_file = csv.reader(file, delimiter="\t")
        next(tsv_file)

        for line in tsv_file:
            print(line)


def reify_edges(g: Graph, model: Model) -> Graph:
    """
    Reify all edges in *g* that have reifications in *model*.

    Args:
        g: a :class:`~penman.graph.Graph` object
        model: a model defining reifications
    Returns:
        A new :class:`~penman.graph.Graph` object with reified edges.
    Example:
        >>> from penman.codec import PENMANCodec
        >>> from penman.models.amr import model
        >>> from penman.transform import reify_edges
        >>> codec = PENMANCodec(model=model)
        >>> g = codec.decode('(c / chapter :mod 7)')
        >>> g = reify_edges(g, model)
        >>> print(codec.encode(g))
        (c / chapter
           :ARG1-of (_ / have-mod-91
                       :ARG2 7))
    """
    vars = g.variables()
    if model is None:
        model = Model()
    new_epidata = dict(g.epidata)
    new_triples: List[BasicTriple] = []
    for triple in g.triples:
        if model.is_role_reifiable(triple[1]):
            in_triple, node_triple, out_triple = model.reify(triple, vars)
            if appears_inverted(g, triple):
                in_triple, out_triple = out_triple, in_triple
            var = node_triple[2][0]
            # rename variable if it already exists
            if var in vars:
                for var_idx in range(2, 100):
                    cur_var = "{}{}".format(var, var_idx)
                    if cur_var not in vars:
                        var = cur_var
                        break
            node_triple = (var, node_triple[1], node_triple[2])
            in_triple = (var, in_triple[1], in_triple[2])
            out_triple = (var, out_triple[1], out_triple[2])
            new_triples.extend((in_triple, node_triple, out_triple))
            vars.add(var)
            # manage epigraphical markers
            new_epidata[in_triple] = [Push(var)]
            old_epis = new_epidata.pop(triple) if triple in new_epidata else []
            node_epis, out_epis = _edge_markers(old_epis)
            new_epidata[node_triple] = node_epis
            new_epidata[out_triple] = out_epis
            # we don't know where to put the final POP without configuring
            # the tree; maybe this should be a tree operation?
        else:
            new_triples.append(triple)

    g = Graph(new_triples,
              epidata=new_epidata,
              metadata=g.metadata)
    logger.info('Reified edges: %s', g)
    return g


def reify_amr(amr):
    codec = PENMANCodec(model=model)
    g = codec.decode(amr)
    g = reify_edges(g, model)
    reified_amr = codec.encode(g)
    return reified_amr


if __name__ == "__main__":
    read_mappings(MAPPING_FILE_PATH)

