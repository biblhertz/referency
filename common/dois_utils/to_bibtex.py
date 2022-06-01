import os

from isbnlib import meta
from isbnlib.registry import bibformatters

from common.misc import fields


def to_bibtex(outpath, references):
    """
    Return a the path to a file containing bibtex metadata for a given list of references.
    """
    bibtex = bibformatters["bibtex"]
    bib = ''

    for ref in references:
        if fields.ISBN in ref and ref[fields.ISBN]:
            try:
                bib += bibtex(meta(ref[fields.ISBN], service="goob")) + '\n'
            except Exception as e:
                pass
    outfile = os.path.join(outpath, 'citations.bib')

    with open(file=outfile, mode="w", encoding="UTF-8") as fd:
        fd.write(bib)

    return outfile
