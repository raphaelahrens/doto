#!/usr/bin/env roundup
#
# Test the functionality of the doto CLI.
# --------
# 
# Every test function starts with "it_".

# `describe` the plan meaningfully.
describe "Test the functionality of the doto CLI."

before() {
    export DOTO_CONFIG=./test/configs/dotorc.1
    export PATH="$PATH:."
    IN_TWO_DAYS="$(python3 ./test/date_util.py 2 0 0)"
    IN_ONE_WEEK="$(python3 ./test/date_util.py 7 0 0)"
    IN_ONE_HOUR="$(python3 ./test/date_util.py 0 1 0)"
}

it_runs_add_task() {
    $COVERAGE doto task add "title" "description"
}

it_runs_add_task_with_due() {
    $COVERAGE doto task add "title" "description" --due $IN_TWO_DAYS
}

it_runs_add_task_with_difficulty() {
    $COVERAGE doto task add "title" "description" --difficulty 0
    $COVERAGE doto task add "title" "description" --difficulty 1
    $COVERAGE doto task add "title" "description" --difficulty 2
    $COVERAGE doto task add "title" "description" --difficulty 3
    $COVERAGE doto task add "title" "description" --difficulty 4
}

it_runs_apmt() {
    $COVERAGE doto apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS"
}

it_runs_apmt_with_description() {
    $COVERAGE doto apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS" --description "long description"
}

it_runs_apmt_with_end() {
    $COVERAGE doto apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS" --end $IN_ONE_WEEK
}

it_fails_apmt_with_end_lt() {
    test 5 -eq $($COVERAGE doto apmt add "Appointment" "$IN_ONE_WEEK" --end $IN_TWO_DAYS > /dev/null; echo $?)
}

it_runs_add_task_with_UTF() {
    $COVERAGE doto task add "äöüß@ł€¶ŧ←↓→øþæſðæſðđŋħ" "öäüßµ”“đŋŧ←↓→øĸħððŋđŧ" --difficulty 0
}

it_fails_with_wrong_difficulty() {
    test 2 -eq $($COVERAGE doto task add "title" "description" --difficulty 5;    echo $?)
    test 2 -eq $($COVERAGE doto task add "title" "description" --difficulty 1235; echo $?)
    test 2 -eq $($COVERAGE doto task add"title" "description" --difficulty -1;   echo $?)
}

# List all events
it_runs_ls_all() {
    $COVERAGE doto ls --all
}

# List all open tasks
it_runs_ls() {
    $COVERAGE doto ls
    $COVERAGE doto ls tasks
    $COVERAGE doto ls apmts
    $COVERAGE doto ls overview
}

it_runs_start() {
    doto ls tasks
    $COVERAGE doto task start 3
}

it_runs_reset() {
    doto ls tasks
    $COVERAGE doto task reset 3
}

#Finish task 0
it_runs_start_done_reset() {
    doto ls tasks
    $COVERAGE doto task start 0
    $COVERAGE doto task done 0
    $COVERAGE doto task reset 0
}

it_runs_show() {
    doto ls tasks
    $COVERAGE doto task show 1
    $COVERAGE doto task show 2
}

it_runs_modify() {
    doto ls tasks
    $COVERAGE doto task modify 1 --title "LOL"
    $COVERAGE doto task modify 2 --description "A description"
    $COVERAGE doto task modify 2 --description "A description"
    $COVERAGE doto task modify 2 --due "2020.12.12-11:30"
    $COVERAGE doto task modify 2 --difficulty 0
}

it_runs_modify_RESET() {
    doto ls tasks
    $COVERAGE doto task modify 2 --due RESET
    $COVERAGE doto task modify 2 --difficulty 0
}

#Finish task 0
it_runs_done() {
    doto ls tasks
    $COVERAGE doto task done 0
}

it_runs_del() {
    doto ls tasks
    $COVERAGE doto task del 0    
}

it_runs_punch() {
    $COVERAGE doto punch in
    $COVERAGE doto punch out
}

it_fails_with_wrong_id() {
    doto ls tasks
    test 1 -eq $($COVERAGE doto task done -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto task start -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto task reset -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto task del -1 > /dev/null; echo $?)
    test 1 -eq $($COVERAGE doto task show -1 > /dev/null; echo $?)
}
it_fails_done_with_already_done() {
    doto ls tasks
    doto task done 0
    test 5 -eq $($COVERAGE doto task done 0 > /dev/null; echo $?)
    test 5 -eq $($COVERAGE doto task start 0 > /dev/null; echo $?)
}

it_fails_with_has_no_cache() {
    doto ls tasks
    rm ./test/store/cache
    test 3 -eq $($COVERAGE doto task done  0 > /dev/null; echo $?)
    test 3 -eq $($COVERAGE doto task start 0 > /dev/null; echo $?)
    test 3 -eq $($COVERAGE doto task reset 0 > /dev/null; echo $?)
    test 3 -eq $($COVERAGE doto task show  0 > /dev/null; echo $?)
    test 3 -eq $($COVERAGE doto task del   0 > /dev/null; echo $?)
}

it_fails_with_has_no_tasks() {
    export DOTO_CONFIG=./test/configs/dotorc.2
    test 2 -eq $($COVERAGE doto task done  0 > /dev/null; echo $?)
    test 2 -eq $($COVERAGE doto task start 0 > /dev/null; echo $?)
    test 2 -eq $($COVERAGE doto task reset 0 > /dev/null; echo $?)
    test 2 -eq $($COVERAGE doto task show  0 > /dev/null; echo $?)
    test 2 -eq $($COVERAGE doto task del   0 > /dev/null; echo $?)
}
