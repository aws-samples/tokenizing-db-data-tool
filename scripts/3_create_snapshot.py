#!/usr/local/bin/python
import os
import sys
from util import *

rds = rds()
stage = os.environ['STAGE']
tmp_db_name = os.environ['TMP_DBID']
tmp_snapshot_name = os.environ['TMP_SNAPSHOT_NAME']
target_aws_account = os.environ['TARGET_AWS_ACCOUNT']

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))
    if find_snapshot(rds, tmp_snapshot_name):
        print(f'{tmp_snapshot_name} already exists, start deleting')
        rds.delete_db_snapshot(
            DBSnapshotIdentifier=tmp_snapshot_name,
        )
        wait(rds, 'db_snapshot_deleted', tmp_snapshot_name)

    print(f'{tmp_snapshot_name} start creating')
    create_snapshot()

@timeit
def create_snapshot():
    snapshot = rds.create_db_snapshot(
        DBInstanceIdentifier=tmp_db_name,
        DBSnapshotIdentifier=tmp_snapshot_name,
    )
    wait(rds, 'db_snapshot_available', tmp_snapshot_name)

    print(f'share {tmp_snapshot_name} to preprod aws...')
    rds.modify_db_snapshot_attribute(
        AttributeName='restore',
        DBSnapshotIdentifier=tmp_snapshot_name,
        ValuesToAdd=[
            target_aws_account,
        ],
    )

main()
