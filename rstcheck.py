#!/usr/bin/env python

"""Check code blocks in ReStructuredText."""

from __future__ import division
from __future__ import unicode_literals

import os
import subprocess
import sys
import tempfile

from docutils.core import publish_cmdline, default_description
from docutils.writers.latex2e import Writer as Latex2eWriter
from docutils.writers.latex2e import LaTeXTranslator
from docutils import nodes
from docutils.parsers.rst import directives, Directive


def node_has_class(node, classes):
    """Return True if node has the specified class."""
    if not (issubclass(type(classes), list)):
        classes = [classes]
    for cname in classes:
        if cname in node['classes']:
            return True
    return False


def node_lang_class(node):
    """Return language specification from a node class names."""
    for cname in node['classes']:
        if cname.startswith('lang-'):
            return cname[5:]
    return None


class CodeBlockDirective(Directive):

    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = False
    option_spec = {
        'linenos': directives.flag,
    }

    def run(self):
        # extract langauge from block or commandline
        # we allow the langauge specification to be optional
        try:
            language = self.arguments[0]
        except IndexError:
            language = 'guess'
        code = '\n'.join(self.content)
        literal = nodes.literal_block(code, code)
        literal['classes'].append('code-block')
        literal['language'] = language
        literal['linenos'] = 'linenos' in self.options
        return [literal]

for _name in ['code-block', 'sourcecode']:
    directives.register_directive(_name, CodeBlockDirective)


class CheckTranslator(LaTeXTranslator):

    def __init__(self, document):
        LaTeXTranslator.__init__(self, document)

    def visit_literal_block(self, node):
        if not node_has_class(node, 'code-block'):
            return

        lang = node.get('language', None)
        if lang is None:
            lang = node_lang_class(node)
        if lang is None:
            lang = self.cb_default_lang

        # TODO: Support other languages. Assume C++ for now.
        output_file = tempfile.NamedTemporaryFile(suffix='.cc', mode='w')
        output_file.write(node.rawsource)
        output_file.flush()

        print(node.rawsource, file=sys.stderr)
        status = '\x1b[32mOkay\x1b[0m'
        try:
            subprocess.check_call(['g++', '-std=c++0x', '-fsyntax-only',
                                   '-Wall', '-Wextra', output_file.name])
        except subprocess.CalledProcessError:
            status = '\x1b[31mError\x1b[0m'

        print(status)

        raise nodes.SkipNode

    def depart_literal_block(self, node):
        pass


class CheckWriter(Latex2eWriter):

    def __init__(self):
        Latex2eWriter.__init__(self)
        self.translator_class = CheckTranslator


def main():
    description = (
        'Checks code blocks. ' +
        default_description)
    publish_cmdline(writer=CheckWriter(), description=description,
                    argv=sys.argv[1:] + [os.devnull])


if __name__ == '__main__':
    main()