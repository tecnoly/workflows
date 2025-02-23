# Copyright Kevin Deldycke <kevin@deldycke.com> and contributors.
# All Rights Reserved.
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.

""" Add all missing contributors from commit history to the ``.mailmap`` file
at the root of repository.

This script will refrain from adding those already registered as aliases.

After the update, we will have the opportunity to identify potential duplicate
identities, and tidying things up by hand-editing the .mailmap file.
"""

from __future__ import annotations

import sys
from pathlib import Path
from subprocess import run
from textwrap import dedent

contributors = set()

# Fetch all variations of authors and commiters.
# For format output syntax, see: https://git-scm.com/docs
#   /pretty-formats#Documentation/pretty-formats.txt-emaNem
for param in ("%aN <%aE>", "%cN <%cE>"):
    process = run(
        ("git", "log", f"--pretty=format:{param}"),
        capture_output=True,
        encoding="utf-8",
    )

    # Parse git CLI output.
    if process.returncode:
        sys.exit(process.stderr)
    for line in process.stdout.splitlines():
        if line.strip():
            contributors.add(line)

# Load-up .mailmap content. Create file if it doesn't exists.
mailmap_file = Path("./.mailmap").resolve()
mailmap_file.touch(exist_ok=True)
content = mailmap_file.read_text()

# Initialize empty .mailmap with pointers to reference documentation.
if not content:
    content = dedent(
        """
        # Format is:
        #   Prefered Name <preferred e-mail>  Other Name <other e-mail>
        #
        # Reference: https://git-scm.com/docs/git-blame#_mapping_authors
        """
    )

# Extract comments in .mailmap header and keep mapping lines.
header_comments = []
mappings = set()
for line in content.splitlines():
    if line.startswith("#"):
        header_comments.append(line)
    elif line.strip():
        mappings.add(line)

# Add all missing contributors to the mail mapping.
for contributor in contributors:
    if contributor not in content:
        mappings.add(contributor)

# Save content to .mailmap file.
mailmap_file.write_text(
    "{}\n\n{}\n".format("\n".join(header_comments), "\n".join(sorted(mappings)))
)
