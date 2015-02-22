#!/usr/bin/env python

import os

def get(cmd):
    return os.popen(cmd).read()[:-1]

R = get("cat recipe.template")

g10 = get("git log --pretty=oneline --reverse | tail -10 | sed 's/^/# /'")
srcrev = get("git log --pretty=oneline --reverse | tail -1 | sed 's/ .*//'")
branch = get("git status | head -1 | cut -c 11-")

print R.replace("__G10", g10).replace("__SRCREV", srcrev).replace("__BRANCH", branch)

