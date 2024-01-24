#!/usr/local/bin/python
import os
import sys
from util import *

stage = os.environ['STAGE']
rds = rds()
origin_db_name = os.environ['ORIGINAL_DBID']
new_origin_db_name = f"{origin_db_name}-new"
tmp_snapshot_name = 'demo-prd-tmp-snapshot'
new_tmp_snapshot_name = f"{tmp_snapshot_name}-new"

@timeit
def main():
    check_stage(stage, os.path.basename(__file__))

    print(f'original DB: {origin_db_name}')
    db = find_db(rds, origin_db_name)
    dbPGroup = db['DBParameterGroups'][0]['DBParameterGroupName']
    dbOGroup = db['OptionGroupMemberships'][0]['OptionGroupName']
    dbSGroupIds = [sg['VpcSecurityGroupId'] for sg in db['VpcSecurityGroups']]
    dbSubnetGroup = db['DBSubnetGroup']['DBSubnetGroupName']

    print(f'target snapshot: {new_tmp_snapshot_name}')

    params = {
        'DBInstanceIdentifier': new_origin_db_name,
        'DBSnapshotIdentifier': new_tmp_snapshot_name,
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
        'MultiAZ': db['MultiAZ'],
        'PubliclyAccessible': db['PubliclyAccessible'],
        'StorageType': db['StorageType'],
        'DBInstanceClass': db['DBInstanceClass'],
        'Tags': db['TagList'],
    }

    print(f'restore params: {params}')
    rds.restore_db_instance_from_db_snapshot(**params)
    wait(rds, 'db_instance_available', new_origin_db_name)

    for role in db['AssociatedRoles']:
        rds.add_role_to_db_instance(
            DBInstanceIdentifier=new_origin_db_name,
            RoleArn=role['RoleArn'],
            FeatureName=role['FeatureName'],
        )

main()
