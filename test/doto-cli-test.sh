#!/usr/bin/env roundup
#
# Test the functionality of the doto CLI.
# --------
# 
# Every test function starts with "it_".

# `describe` the plan meaningfully.
describe "Test the functionality of the doto CLI."

echo "TEST"

# Add a new task
it_runs_add() {
    doto.py add "title" "description"
}

# List all open tasks
it_runs_list() {
    doto.py list
}

it_runs_del() {
    doto.py del 1    
}
