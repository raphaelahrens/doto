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
    $COVERAGE doto add "title" "description"
}

it_runs_add_with_due() {
    $COVERAGE doto add "title" "description" --due 2013.10.15-20:15
}

it_runs_add_with_difficulty() {
    $COVERAGE doto add "title" "description" --difficulty 0
    $COVERAGE doto add "title" "description" --difficulty 1
    $COVERAGE doto add "title" "description" --difficulty 2
    $COVERAGE doto add "title" "description" --difficulty 3
    $COVERAGE doto add "title" "description" --difficulty 4
}

it_runs_add_with_UTF() {
    $COVERAGE doto add "äöüß@ł€¶ŧ←↓→øþæſðæſðđŋħ" "öäüßµ”“đŋŧ←↓→øĸħððŋđŧ" --difficulty 0
}

it_fails_with_wrong_difficulty() {
    test 2 -eq $($COVERAGE doto add "title" "description" --difficulty 5; echo $?)
    test 2 -eq $($COVERAGE doto add "title" "description" --difficulty 1235; echo $?)
    test 2 -eq $($COVERAGE doto add "title" "description" --difficulty -1; echo $?)
}

# List all tasks
it_runs_ls_all() {
    $COVERAGE doto ls --all
}

# List all open tasks
it_runs_ls() {
    $COVERAGE doto ls
}

it_runs_start() {
    $COVERAGE doto start 3
}

it_runs_reset() {
    $COVERAGE doto reset 3
}

#Finish task 0
it_runs_start_done_reset() {
    $COVERAGE doto start 2
    $COVERAGE doto done 2
    $COVERAGE doto reset 2
}

it_runs_show() {
    $COVERAGE doto show 1
    $COVERAGE doto show 2
}

it_runs_modify() {
    $COVERAGE doto modify 1 --title "LOL"
    $COVERAGE doto modify 2 --description "A description"
    $COVERAGE doto modify 2 --description "A description"
    $COVERAGE doto modify 2 --due "2020.12.12-11:30"
    $COVERAGE doto modify 2 --difficulty 0
}

it_runs_modify_RESET() {
    $COVERAGE doto modify 2 --due RESET
    $COVERAGE doto modify 2 --difficulty 0
}

#Finish task 0
it_runs_done() {
    $COVERAGE doto done 0
}

it_runs_del() {
    $COVERAGE doto del 1    
}

it_fails_with_wrong_id() {
    test 1 -eq $($COVERAGE doto done -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto start -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto reset -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto del -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto show -1 > /dev/null; echo $?)
}
it_fails_done_with_already_done() {
    test 5 -eq $($COVERAGE doto done 0 > /dev/null; echo $?)
    test 5 -eq $($COVERAGE doto start 0 > /dev/null; echo $?)
}
