#!/usr/local/bin/python

import os
import sys
from util import *

rds = rds()
origin_db_name = os.environ['ORIGINAL_DBID']
stage = os.environ['STAGE']
tmp_db_name = os.environ['TMP_DBID']
tmp_snapshot_name = os.environ['TMP_SNAPSHOT_NAME']

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))
    if find_db(rds, tmp_db_name):
        print(f'{tmp_db_name} already exists. skip restoring')
    else:
        print(f'{tmp_db_name} not found, start restoring')
        restore()

@timeit
def restore():
    print(f'original DB: {origin_db_name}')
    db = find_db(rds, origin_db_name)
    dbPGroup = db['DBParameterGroups'][0]['DBParameterGroupName']
    dbOGroup = db['OptionGroupMemberships'][0]['OptionGroupName']
    dbSGroupIds = [sg['VpcSecurityGroupId'] for sg in db['VpcSecurityGroups']]
    dbSubnetGroup = db['DBSubnetGroup']['DBSubnetGroupName']

    snapshots = rds.describe_db_snapshots(
        DBInstanceIdentifier=origin_db_name,
    )
    latestSnapshot = snapshots['DBSnapshots'][-1]
    print(f'target snapshot: {latestSnapshot["DBSnapshotIdentifier"]}')

    params = {
        'DBInstanceIdentifier': tmp_db_name,
        'DBSnapshotIdentifier': latestSnapshot['DBSnapshotIdentifier'],
        'DBParameterGroupName': dbPGroup,
        'OptionGroupName': dbOGroup,
        'VpcSecurityGroupIds': dbSGroupIds,
        'DBSubnetGroupName': dbSubnetGroup,
        'AutoMinorVersionUpgrade': db['AutoMinorVersionUpgrade'],
        'AvailabilityZone': db['AvailabilityZone'],
        'BackupTarget': db['BackupTarget'],
        'CopyTagsToSnapshot': True,
        'DeletionProtection': False,
        'EnableCustomerOwnedIp': db['CustomerOwnedIpEnabled'],
        'EnableIAMDatabaseAuthentication': db['IAMDatabaseAuthenticationEnabled'],
        'Engine': db['Engine'],
        'LicenseModel': db['LicenseModel'],
        'MultiAZ': False,
        'PubliclyAccessible': db['PubliclyAccessible'],
        'StorageType': 'gp2',
        'DBInstanceClass': 'db.r5.large',
    }
    print(f'restore params: {params}')
    rds.restore_db_instance_from_db_snapshot(**params)

    wait(rds, 'db_instance_available', tmp_db_name)

main()
