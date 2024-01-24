#!/usr/local/bin/python
import os
import sys
from util import *

stage = os.environ['STAGE']
rds = rds()
origin_db_name = os.environ['ORIGINAL_DBID']
new_origin_db_name = f"{origin_db_name}-new"

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))

    print(f'original DB: {origin_db_name}')
    db = find_db(rds, origin_db_name)

    if db['DeletionProtection']:
        rds.modify_db_instance(
            ApplyImmediately=True,
            DBInstanceIdentifier=origin_db_name,
            DeletionProtection=False,
        )
        wait(rds, 'db_instance_available', origin_db_name)

    # delete original DB
    delete_db(rds, origin_db_name, False)

    # rename new to original DB
    rds.modify_db_instance(
        ApplyImmediately=True,
        DBInstanceIdentifier=new_origin_db_name,
        NewDBInstanceIdentifier=origin_db_name,
    )
    print(f'waiting {new_origin_db_name} => {origin_db_name} modifying...')
    wait(rds, 'db_instance_available', new_origin_db_name)

main()
