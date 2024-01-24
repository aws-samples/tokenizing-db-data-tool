#!/usr/local/bin/python
import os
import sys
from util import *

rds = rds()
stage = os.environ['STAGE']
region = os.environ['REGION']
source_aws_account = os.environ['SOURCE_AWS_ACCOUNT']
tmp_snapshot_name = os.environ['TMP_SNAPSHOT_NAME']
source_tmp_snapshot_arn = f"arn:aws:rds:{region}:{source_aws_account}:snapshot:{tmp_snapshot_name}"
target_tmp_snapshot_name = f"{tmp_snapshot_name}-new"

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))

    if find_snapshot(rds, target_tmp_snapshot_name):
        print(f'{target_tmp_snapshot_name} already exists, start deleting')
        rds.delete_db_snapshot(
            DBSnapshotIdentifier=target_tmp_snapshot_name,
        )
        wait(rds, 'db_snapshot_deleted', target_tmp_snapshot_name)

    params = {
        'SourceDBSnapshotIdentifier': source_tmp_snapshot_arn,
        'TargetDBSnapshotIdentifier': target_tmp_snapshot_name,
    }
    print(f"copy params: {params}")
    snapshots = rds.copy_db_snapshot(**params)
    wait(rds, 'db_snapshot_available', target_tmp_snapshot_name)

main()
