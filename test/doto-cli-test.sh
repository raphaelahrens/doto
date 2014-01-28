#!/usr/bin/env roundup
#
# Test the functionality of the doto CLI.
# --------
# 
# Every test function starts with "it_".

# `describe` the plan meaningfully.
describe "Test the functionality of the doto CLI."

# Add a new task
it_runs_add() {
    doto.py add "title" "description"
}

it_runs_addi_with_due() {
    doto.py add "title" "description" --due 2013.10.15-20:15
}

it_runs_add_with_difficulty() {
    doto.py add "title" "description" --difficulty 0
    doto.py add "title" "description" --difficulty 1
    doto.py add "title" "description" --difficulty 2
    doto.py add "title" "description" --difficulty 3
    doto.py add "title" "description" --difficulty 4
}

it_fails_with_wrong_difficulty() {
    test 2 -eq $(doto.py add "title" "description" --difficulty 5; echo $?)
    test 2 -eq $(doto.py add "title" "description" --difficulty 1235; echo $?)
    test 2 -eq $(doto.py add "title" "description" --difficulty -1; echo $?)
}

# List all open tasks
it_runs_ls() {
    doto.py ls
}

it_runs_ls_all() {
    doto.py ls --all
}

it_runs_del() {
    doto.py del 1    
}
