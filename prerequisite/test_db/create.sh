#!/bin/bash

tables=('load_departments' 'load_dept_emp' 'load_dept_manager' 'load_employees' 'load_salaries1' 'load_salaries2' 'load_salaries3' 'load_titles')
sqls=('show_elapsed' 'objects' 'employees' 'create_table_only')

PRD_DB_ENDPOINT='YOUR_PRD_DB_ENDPOINT'
DB_USER='YOUR_DB_USER'
DB_PASS='YOUR_DB_PASS'

for table in "${tables[@]}";do
    wget https://raw.githubusercontent.com/datacharmer/test_db/master/${table}.dump
done

for sql in "${sqls[@]}";do
    wget https://raw.githubusercontent.com/datacharmer/test_db/master/${sql}.sql
done

mysql -h$PRD_DB_ENDPOINT -u$DB_USER -p$DB_PASS < employees.sql

rm *.sql
rm *.dump

