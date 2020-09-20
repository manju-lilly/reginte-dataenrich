#!/usr/bin/env python3

import os

import re

"""for f in os.listdir("data"):
    if f.endswith(".txt"):
        filepath = os.path.join(f"data/{f}")
        lines = open(filepath, 'r').readlines()
        es = ExtractSection(lines)
        lines = es.extract_clinical_studies()
    write_path = os.path.join("data", "clinicalstudies", os.path.basename(f))
    with open(write_path, 'w') as w:
        w.write(lines)

"""
