"""Configuration file for the Sphinx documentation builder."""
# pylint: disable=C0103
import os
import re
import typing as t
from datetime import date
from importlib.util import find_spec
from pathlib import Path

import sphinx_rtd_theme  # type: ignore[import]
from sphinx.application import Sphinx


try:
    from importlib.metadata import metadata  # pylint: disable=ungrouped-imports
except ModuleNotFoundError:  # pragma: py-gte-38
    from importlib_metadata import metadata  # type: ignore[import,no-redef]


needs_sphinx = "3.1"  #: Minimum Sphinx version to build the docs


#: -- GLOB VARS ------------------------------------------------------------------------
NOT_LOADED_MSGS = []


#: -- PROJECT INFORMATION --------------------------------------------------------------
project = "rstcheck"
author = "Steven Myint <git@stevenmyint.com>"
GH_REPO_LINK = "https://github.com/rstcheck/rstcheck"
CREATION_YEAR = 2013
CURRENT_YEAR = f"{date.today().year}"
copyright = (  # noqa: VNE003 # pylint: disable=W0622
    f"{CREATION_YEAR}{('-' + CURRENT_YEAR) if CURRENT_YEAR != CREATION_YEAR else ''}, "
    + f"{author} and AUTHORS"
)
RSTCHECK_VERSION = metadata(project)["Version"]
release = RSTCHECK_VERSION  #: The full version, including alpha/beta/rc tags
version_parts = re.search(r"^v?(?P<version>\d+\.\d+)\.\d+[-.]?(?P<tag>[a-z]*)[\.]?\d*", release)
#: Major + Minor version like (X.Y)
version = None if not version_parts else version_parts.group("version")
#: only tags like alpha/beta/rc
RELEASE_LEVEL = None if not version_parts else version_parts.group("tag")


#: -- GENERAL CONFIG -------------------------------------------------------------------
extensions: t.List[str] = []
today_fmt = "%Y-%m-%d"
exclude_patterns: t.List[str] = []  #: Files to exclude for source of doc

#: Added dirs for static and template files if they exist
html_static_path = ["_static"] if Path("_static").exists() else []
templates_path = ["_templates"] if Path("_templates").exists() else []

rst_prolog = """
.. ifconfig:: RELEASE_LEVEL in ('alpha', 'beta', 'rc')

   .. warning::
      The here documented release |release| is a pre-release.
      Keep in mind that breaking changes can occur till the final release.

      You may want to use the latest stable release instead.
"""

rst_epilog = """
.. |br| raw:: html

    <br/>
"""

tls_cacerts = os.getenv("SSL_CERT_FILE")


#: -- M2R2 -----------------------------------------------------------------------------
extensions.append("m2r2")
source_suffix = [".rst", ".md"]


#: -- LINKCHECK CONFIG -----------------------------------------------------------------
#: 1 Worker 5 Retries to fix 429 error
linkcheck_workers = 1
linkcheck_retries = 5
linkcheck_timeout = 30


#: -- DEFAULT EXTENSIONS ---------------------------------------------------------------
#: Global
extensions.append("sphinx.ext.duration")
extensions.append("sphinx.ext.coverage")  #: sphinx-build -b coverage ...
coverage_write_headline = False
coverage_show_missing_items = True
extensions.append("sphinx.ext.doctest")  #: sphinx-build -b doctest ...

#: ReStructuredText
extensions.append("sphinx.ext.autosectionlabel")
autosectionlabel_prefix_document = True
autosectionlabel_maxdepth = 2
extensions.append("sphinx.ext.ifconfig")
extensions.append("sphinx.ext.viewcode")

#: Links
extensions.append("sphinx.ext.intersphinx")
# NOTE: to inspect .inv files: https://github.com/bskinn/sphobjinv
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "pattern": ("https://docs.python.org/3/library/", "objects.pattern.inv"),
}

extensions.append("sphinx.ext.extlinks")
extlinks = {
    "repo": (f"{GH_REPO_LINK}/%s", "Repo's %s"),
    "issue": (f"{GH_REPO_LINK}/issues/%s", "#%s"),
    "pull": (f"{GH_REPO_LINK}/pull/%s", "PR#%s"),
    "user": ("https://github.com/%s", "@%s"),
}


#: -- CLICK ----------------------------------------------------------------------------
extensions.append("sphinx_click.ext")


#: -- SPELLING -------------------------------------------------------------------------
spelling_word_list_filename = "spelling_dict.txt"
spelling_show_suggestions = True

if find_spec("sphinxcontrib.spelling") is not None:
    extensions.append("sphinxcontrib.spelling")
else:
    NOT_LOADED_MSGS.append("## 'sphinxcontrib-spelling' extension not loaded - not installed")


#: -- HTML THEME -----------------------------------------------------------------------
#: needs install: "sphinx-rtd-theme"
extensions.append("sphinx_rtd_theme")
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_theme_options = {"style_external_links": True, "navigation_depth": 5}


#: -- HTML OUTPUT ----------------------------------------------------------------------
html_last_updated_fmt = today_fmt
html_show_sourcelink = True  #: Add links to *.rst source files on HTML pages


#: -- FINAL SETUP ----------------------------------------------------------------------
def setup(app: Sphinx) -> None:
    """Connect custom func to sphinx events."""
    app.add_config_value("RELEASE_LEVEL", "", "env")


for msg in NOT_LOADED_MSGS:
    print(msg)
