#!/bin/bash

# Report names in the APPN context that are also found in the standard RO-Crate context.

# appn_terms is a pipe-delimited list of class and property names from context.json (the APPN context)
appn_terms=`sed -nE -e '/@context/,$ p' context.json | sed -nE -e 's/^\s*"(\w+)".*/\1/p' | tr '\n' '|' | sed -e 's/.$//'`

# This pipe 1) ignores rows before the "@context" element, 2) extracts names from the remaining lines, and 3) prints any names also found in appn_terms
sed -nE -e '/@context/,$ p' ro-crate_1.1_context.json | sed -nE -e 's/^\s*"(\w+)".*/\1/p' | sed -nE -e "/^($appn_terms)$/p"
