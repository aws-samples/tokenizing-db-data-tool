#!/usr/local/bin/python
import os
import sys
from util import *

rds = rds()
tmp_db_name = os.environ['TMP_DBID']
stage = os.environ['STAGE']

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))
    delete_db(rds, tmp_db_name, True)

main()
