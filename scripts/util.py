#!/usr/local/bin/python

import os
import sys
import time
import boto3
from datetime import datetime
from botocore.config import Config

def aws_config():
    return Config(region_name = os.environ['REIGON'])

def rds():
    return boto3.client('rds', config=aws_config())

def ssm():
    return boto3.client('ssm', config=aws_config())

def sm():
    return boto3.client('secretsmanager', config=aws_config())

def sm_get(sid):
    return sm().get_secret_value(
        SecretId=sid
    )

def ssm_get(name):
    return ssm().get_parameter(
        Name=name,
        WithDecryption=False
    )['Parameter']['Value']

def find_snapshot(rds, name):
    try:
        snapshots = rds.describe_db_snapshots(
            DBSnapshotIdentifier=name,
        )
        print(f'snapshot {name} found')
        return snapshots['DBSnapshots'][0]
    except rds.exceptions.DBSnapshotNotFoundFault:
        print(f'{name} not found')
        return None

def find_db(rds, name):
    try:
        dbs = rds.describe_db_instances(
            DBInstanceIdentifier=name
        )
        print(f'DB {name} found.')
        return dbs['DBInstances'][0]
    except rds.exceptions.DBInstanceNotFoundFault:
        print(f'DB {name} not found.')
        return None

def delete_db(rds, name, clean=False):
    if not find_db(rds, name):
        print(f'{name} not found. skip delete')
        return
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    params = {
        'DBInstanceIdentifier': name,
        'DeleteAutomatedBackups': clean,
        'SkipFinalSnapshot': clean,
    }
    if not clean:
        params['FinalDBSnapshotIdentifier'] = f"{name}-{timestamp}"
    rds.delete_db_instance(**params)
    wait(rds, 'db_instance_deleted', name)
    print(f'{name} deleted')

def wait(rds, status, name):
    p = {}
    if status.startswith('db_snapshot'):
        p['DBSnapshotIdentifier'] = name
    elif status.startswith('db_instance'):
        p['DBInstanceIdentifier'] = name
    else:
        raise f"invalid status: {status}"
    p['WaiterConfig'] = {
        'Delay': 60,
        'MaxAttempts': 300
    }
    print(f'waiting {name} to be {status}...')
    waiter = rds.get_waiter(status)
    waiter.wait(**p)
    print(f'{name} changed to {status}')

def check_stage(stage, script_name):
    creator_names = [
        '1_restore_from_snapshot.py',
        '2_db_tokenization.py',
        '3_create_snapshot.py',
        '4_delete_tmp_db.py',
        '5_notify.py',
    ]
    importer_names = [
        '6_copy_snapshot.py',
        '7_restore_from_snapshot.py',
        '8_rename.py',
    ]
    error = f"you can't run {script_name} on {stage}"
    if stage in ['prod'] and script_name not in creator_names:
        raise error
    elif stage in ['preprod'] and script_name not in importer_names:
        raise error

def timeit(f):
    def timed(*args, **kw):
        ts = time.time()
        result = f(*args, **kw)
        te = time.time()
        print(f'Function: {f.__name__}')
        print(f'*  args: {args}')
        print(f'*  kw: {kw}')
        print(f'*  execution time: {(te-ts)*1000:8.2f} ms')
        return result
    return timed
