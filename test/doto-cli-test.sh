#!/usr/bin/env roundup
#
# Test the functionality of the doto CLI.
# --------
# 
# Every test function starts with "it_".

# `describe` the plan meaningfully.
describe "Test the functionality of the doto CLI."

init() {
    export DOTO_CONFIG=./test/configs/dotorc.1
}

# Add a new task
it_runs_add() {
    doto add "title" "description"
}

it_runs_add_with_due() {
    doto add "title" "description" --due 2013.10.15-20:15
}

it_runs_add_with_difficulty() {
    doto add "title" "description" --difficulty 0
    doto add "title" "description" --difficulty 1
    doto add "title" "description" --difficulty 2
    doto add "title" "description" --difficulty 3
    doto add "title" "description" --difficulty 4
}

it_runs_add_with_UTF() {
    doto add "äöüß@ł€¶ŧ←↓→øþæſðæſðđŋħ" "öäüßµ”“đŋŧ←↓→øĸħððŋđŧ" --difficulty 0
}

it_fails_with_wrong_difficulty() {
    test 2 -eq $(doto add "title" "description" --difficulty 5; echo $?)
    test 2 -eq $(doto add "title" "description" --difficulty 1235; echo $?)
    test 2 -eq $(doto add "title" "description" --difficulty -1; echo $?)
}

# List all tasks
it_runs_ls_all() {
    doto ls --all
}

# List all open tasks
it_runs_ls() {
    doto ls
}

it_runs_start() {
    doto start 3
}

#Finish task 0
it_runs_start_and_done() {
    doto start 2
    doto done 2
}

it_runs_show() {
    doto show 1
    doto show 2
}

#Finish task 0
it_runs_done() {
    doto done 0
}

it_runs_del() {
    doto del 1    
}

it_fails_done_with_wrong_id() {
    test 1 -eq $(doto done -1 > /dev/null; echo $?)
}
it_fails_done_with_already_done() {
    test 5 -eq $(doto done 0 > /dev/null; echo $?)
}
