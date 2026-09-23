#!/usr/bin/env python3
"""Verify that every relative link in skills/*/SKILL.md resolves inside the plugin.

For each markdown link (outside fenced code blocks) that is not an external
URL, checks that the target file exists and, when a #fragment is given, that
the target document has a heading with that GitHub-flavoured markdown anchor.
Also checks that every SKILL.md starts with valid name/description frontmatter.

Exit status is 1 if anything is broken.
"""

import glob
import os
import re
import sys
import urllib.parse

from build_plugin import LINK_RE, gfm_anchors, iter_outside_fences

ROOT = os.path.dirname(os.path.abspath(__file__))
FRONTMATTER_RE = re.compile(
    r'\A---\nname: ([a-z0-9-]+)\ndescription: "((?:[^"\\\n]|\\.)+)"\n---\n')


def main() -> int:
    anchors_cache = {}
    checked = broken = 0
    problems = []

    def anchors_of(path):
        if path not in anchors_cache:
            with open(path, encoding="utf-8") as f:
                anchors_cache[path] = set(gfm_anchors(f.read().split("\n")).values())
        return anchors_cache[path]

    skill_files = sorted(glob.glob(os.path.join(ROOT, "skills", "*", "SKILL.md")))
    for path in skill_files:
        rel = os.path.relpath(path, ROOT)
        with open(path, encoding="utf-8") as f:
            text = f.read()
        m = FRONTMATTER_RE.match(text)
        if not m or m.group(1) != os.path.basename(os.path.dirname(path)):
            problems.append(f"{rel}: invalid or mismatched frontmatter")
        for lineno, line, in_fence in iter_outside_fences(text.split("\n")):
            if in_fence:
                continue
            for lm in LINK_RE.finditer(line):
                target = lm.group(3)
                if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("//"):
                    continue  # external
                checked += 1
                file_part, _, frag = target.partition("#")
                dest = path if not file_part else os.path.normpath(
                    os.path.join(os.path.dirname(path), urllib.parse.unquote(file_part)))
                err = None
                if not os.path.isfile(dest):
                    err = "missing file"
                elif not dest.startswith(os.path.join(ROOT, "skills") + os.sep):
                    err = "points outside skills/"
                elif frag:
                    if not dest.endswith(".md"):
                        err = "fragment on non-markdown file"
                    elif urllib.parse.unquote(frag) not in anchors_of(dest):
                        err = "missing anchor"
                if err:
                    broken += 1
                    problems.append(f"{rel}:{lineno + 1}: {err}: {target}")

    for p in problems:
        print(p)
    print(f"{len(skill_files)} skills, {checked} relative links checked, "
          f"{broken} broken, {len(problems) - broken} frontmatter problems")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
