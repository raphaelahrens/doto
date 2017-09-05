#!/usr/bin/env roundup
#
# Test the functionality of the doto CLI.
# --------
# 
# Every test function starts with "it_".

describe "Test the functionality of the doto CLI."

before() {
    export DOTO_CONFIG=./test/configs/dotorc.1
    export PATH="$PATH:."
    IN_TWO_DAYS="$(python3 ./test/date_util.py 2 0 0)"
    IN_ONE_WEEK="$(python3 ./test/date_util.py 7 0 0)"
    IN_ONE_HOUR="$(python3 ./test/date_util.py 0 1 0)"
}

it_runs_add_task() {
    $DOTO task add "title" "description"
    $DOTO task show -1
}

it_runs_add_task_with_due() {
    $DOTO task add "title" "description" --due "$IN_TWO_DAYS"
    $DOTO task show -1
}

it_runs_add_task_with_difficulty() {
    $DOTO task add "title" "description" --difficulty 0
    $DOTO task show -1
    $DOTO task add "title" "description" --difficulty 1
    $DOTO task show -1
    $DOTO task add "title" "description" --difficulty 2
    $DOTO task show -1
    $DOTO task add "title" "description" --difficulty 3
    $DOTO task show -1
    $DOTO task add "title" "description" --difficulty 4
    $DOTO task show -1
}

it_runs_apmt() {
    $DOTO apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS"
    $DOTO apmt show -1
}

it_runs_apmt_with_description() {
    $DOTO apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS" --description "long description"
    $DOTO apmt show -1
}

it_runs_apmt_with_end() {
    $DOTO apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS" --end "$IN_ONE_WEEK"
    $DOTO apmt show -1
}

it_fails_apmt_with_end_lt() {
    test 5 -eq "$($DOTO apmt add "Appointment" "$IN_ONE_WEEK" --end "$IN_TWO_DAYS" > /dev/null; echo $?)"
}

it_runs_apmt_with_repeat() {
    $DOTO apmt add "Appointment made on $(date +%d.%m.%y-%H:%M)" "$IN_TWO_DAYS" --repeat @hourly
    $DOTO apmt show -1
}

it_runs_add_task_with_UTF() {
    $DOTO task add 'äöüß@ł€¶ŧ←↓→øþæðæſðđŋħ' 'öäüßµ”“đŋŧ←↓→øĸħððŋđŧ' --difficulty 0
    $DOTO task show -1
}

it_fails_with_wrong_difficulty() {
    test 2 -eq "$($DOTO task add "title" "description" --difficulty 5;    echo $?)"
    test 2 -eq "$($DOTO task add "title" "description" --difficulty 1235; echo $?)"
    test 2 -eq "$($DOTO task add"title" "description" --difficulty -1;   echo $?)"
}

# List all events
it_runs_ls_all() {
    $DOTO ls --all
}

# List all open tasks
it_runs_ls() {
    $DOTO ls
    $DOTO ls tasks
    $DOTO ls apmts
    $DOTO ls overview
}

it_runs_start() {
    $DOTO ls tasks
    $DOTO task start 3
}

it_runs_reset() {
    $DOTO ls tasks
    $DOTO task reset 3
}

#Finish task 0
it_runs_start_done_reset() {
    $DOTO ls tasks
    $DOTO task start 0
    $DOTO task "done" 0
    $DOTO task reset 0
}

it_runs_show() {
    $DOTO ls tasks
    $DOTO task show 1
    $DOTO task show 2
}

it_runs_modify() {
    $DOTO ls tasks
    $DOTO task modify 1 --title "LOL"
    $DOTO task modify 2 --description "A description"
    $DOTO task modify 2 --description "A description"
    $DOTO task modify 2 --due "2020.12.12-11:30"
    $DOTO task modify 2 --difficulty 0
}

it_runs_modify_RESET() {
    $DOTO ls tasks
    $DOTO task modify 2 --due RESET
    $DOTO task modify 2 --difficulty 0
}

#Finish task 0
it_runs_done() {
    $DOTO ls tasks
    $DOTO task "done" 0
}

it_runs_del() {
    $DOTO ls tasks
    $DOTO task del 0    
}

it_runs_punch() {
    $DOTO punch in
    $DOTO punch out
}

it_fails_with_wrong_id() {
    $DOTO ls tasks
    test 1 -eq "$($DOTO task done -2 > /dev/null; echo $?)"
    test 1 -eq "$($DOTO task start -2 > /dev/null; echo $?)"
    test 1 -eq "$($DOTO task reset -2 > /dev/null; echo $?)"
    test 1 -eq "$($DOTO task del -2 > /dev/null; echo $?)"
    test 1 -eq "$($DOTO task show -2 > /dev/null; echo $?)"
}
it_fails_done_with_already_done() {
    $DOTO ls tasks
    $DOTO task "done" 0
    test 5 -eq "$($DOTO task "done" 0 > /dev/null; echo $?)"
    test 5 -eq "$($DOTO task start 0 > /dev/null; echo $?)"
}

it_fails_with_has_no_cache() {
    $DOTO ls tasks
    rm ./test/store/cache
    test 3 -eq "$($DOTO task "done"  0 > /dev/null; echo $?)"
    test 3 -eq "$($DOTO task start 0 > /dev/null; echo $?)"
    test 3 -eq "$($DOTO task reset 0 > /dev/null; echo $?)"
    test 3 -eq "$($DOTO task show  0 > /dev/null; echo $?)"
    test 3 -eq "$($DOTO task del   0 > /dev/null; echo $?)"
}

it_fails_with_has_no_tasks() {
    export DOTO_CONFIG=./test/configs/dotorc.2
    test 2 -eq "$($DOTO task "done"  0 > /dev/null; echo $?)"
    test 2 -eq "$($DOTO task start 0 > /dev/null; echo $?)"
    test 2 -eq "$($DOTO task reset 0 > /dev/null; echo $?)"
    test 2 -eq "$($DOTO task show  0 > /dev/null; echo $?)"
    test 2 -eq "$($DOTO task del   0 > /dev/null; echo $?)"
}
