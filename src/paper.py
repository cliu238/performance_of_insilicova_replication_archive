from __future__ import print_function
from collections import namedtuple
import re
import os
import sys

import jinja2
import jinja2.meta
import yaml

from map_insilico import INSILICO_CAUSE_MAP
from download import load_ghdx_data
from annex_tables import prep_icds


PAPER_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        '..', 'paper')

SECTIONS = [
    'header',
    'abstract',
    'intro',
    'methods',
    'results',
    'table_ccc',
    'table_cccsmf',
    'table_adult_ccc',
    'table_child_ccc',
    'table_neonate_ccc',
    'table_sens_spec',
    'discussion',
    'footer',
]

TABLES = [s for s in SECTIONS if s.startswith('table_')]
FIGURES = [s for s in SECTIONS if s.startswith('figure_')]


def get_adult_cause34_mapping():
    df = load_ghdx_data('adult')[['gs_text34', 'gs_text46']].drop_duplicates()
    return dict(zip(df.gs_text46, df.gs_text34))


def render():
    """Convert the multiple sections and tables into a single markdown file."""
    print('Rendering markdown version of paper...', end='')
    sys.stdout.flush()

    templates_dir = os.path.join(PAPER_DIR, 'templates')
    loader = jinja2.FileSystemLoader(templates_dir)
    env = jinja2.Environment(loader=loader, undefined=jinja2.StrictUndefined)

    # Add the lists of tables and figures to the rendering environment.
    # Tables and figures are referenced by key (the string in the list)
    # and the number in the rendered text is calculated as the index of
    # the key in this list + 1 (since python is 0-indexed)
    env.globals['tables'] = TABLES
    env.globals['figures'] = FIGURES

    outfile = os.path.join(PAPER_DIR, 'paper.md')

    with open(outfile, 'w', encoding='utf8') as f:
        for section in SECTIONS:
            template = '{}.md'.format(section)
            if os.path.exists(os.path.join(PAPER_DIR, 'templates', template)):
                if section in ['header', 'footer']:
                    context = get_metadata_context()
                else:
                    context = get_section_context(section)

                # Fill values which are missing from the context dict with
                # a sentinel value to make drafts more readable.
                with open(os.path.join(templates_dir, template)) as t:
                    tmpstring = t.read()
                ast = env.parse(tmpstring)
                keys = jinja2.meta.find_undeclared_variables(ast)
                for k in keys:
                    if k not in context:
                        context[k] = 'XXX'

                # Lancet requires decimal points be midline instead of baseline
                # post-process the rendered text
                f.write(env.get_template(template).render(context))
                f.write('\n\n')
            else:
                print('{}.md not found'.format(section))

    path = os.path.join(PAPER_DIR, 'additional_file1.md')
    adult_cause_map = get_adult_cause34_mapping()
    icds = prep_icds()
    with open(path, 'w', encoding='utf8') as f:
        context = {}
        for mod in ('adult', 'child', 'neonate'):
            context[mod] = []

            icds_ = icds.loc[mod.title()].sort_values()
            order = icds_.index.tolist()
            causes = sorted(INSILICO_CAUSE_MAP[mod].items(),
                            key=lambda x: order.index(x[0]))

            for cause46, cause_insilico in causes:
                if mod == 'adult':
                    context[mod].append([
                        icds_.get(cause46, ''),
                        cause46,
                        adult_cause_map[cause46],
                        cause_insilico
                    ])
                else:
                    context[mod].append([
                        icds_.get(cause46, ''),
                        cause46,
                        cause_insilico,
                    ])
        f.write(env.get_template('additional_file1.md').render(context))
    print(' done')


"""
pandoc --filter pandoc-citeproc --bibliography=paper\references.bib
--csl paper\citation-style-vancouver-brackets.csl  paper\paper.md
paper\metadata.yml -o paper\drafts\paper.docx

"""


def get_metadata_context():
    """Get the context dict for the header and footer sections."""
    with open(os.path.join(PAPER_DIR, 'metadata.yml')) as f:
        metadata = yaml.load(f)
    authors, affiliations = format_author_list(metadata['authors'],
                                               metadata['affiliations'])
    corr_email, corr_initials = get_corresponding_author(metadata['authors'])
    return {
        'title': metadata['title'],
        'authors': authors,
        'affiliations': affiliations,
        'correspondance_email': corr_email,
        'correspondance_initials': corr_initials,
    }


def get_section_context(section):
    """Get the context dict for a section from a corresponding yaml file."""
    datafile = os.path.join(PAPER_DIR, 'numbers', '{}.yml'.format(section))
    if os.path.exists(datafile):
        with open(datafile) as f:
            context = yaml.load(f)
        return context
    else:
        return {}


def format_author_list(authors, affiliations):
    """Format the author list for the jinja context.

    Args:
        authors (list of dicts): author records with name, affiliation, email
        affil (dict): mapping affiliation key to full instituation name

    Returns:

        * authors (list of tuples)
        * affilations (list of str)
    """
    # Create a list of affiliations. These should appear in the same order as
    # the author and are used to add footnotes to authors.
    affils = []
    for author in authors:
        affil = author['affiliation']
        if affil not in affils:
            affils.append(affil)

    # Look up the position of the affiliated institution to add the
    # appropriate footnote
    Author = namedtuple('Author', ['name', 'notes', 'email'])
    auth_list = []
    for author in authors:
        affil = author['affiliation']
        affil_num = affils.index(affil) + 1
        notes = '^{}^'.format(affil_num)
        if 'corresponding_author' in author and author['corresponding_author']:
            notes = '{}*'.format(notes)
        entry = Author(author['name'], notes, author['email'])
        auth_list.append(entry)

    # Create the list of affiliation footnotes
    affil_list = []
    for i, affil in enumerate(affils):
        institution = affiliations[affil]
        entry = "^{}^ {}".format((i + 1), institution)
        affil_list.append(entry)

    return auth_list, affil_list


def get_corresponding_author(authors):
    """Get the email and initials of the corresponding author."""
    corr_author = []
    for author in authors:
        if 'corresponding_author' in author and author['corresponding_author']:
            corr_author.append(author)
    assert len(corr_author) == 1
    corr_author = corr_author[0]
    return corr_author['email'], get_initials(corr_author['name'])


def get_initials(name):
    """Return the intials from a string."""
    return ''.join([x[0].upper() for x in name.split()])


def get_contributions(authors):
    pass


if __name__ == '__main__':
    render()
