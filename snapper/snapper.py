import boto3
import botocore
import click


session = boto3.Session(profile_name='cloudsnap')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
        filters = [{'Name':'tag:Project', 'Values':[project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshot(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'

## Top level Click group
@click.group()
def cli():
    """cloudsnap cli"""


## Commands for Volumes
@cli.group('volumes')
def volumes():
    """Commands for Volumes"""

@volumes.command('list')
@click.option('--project', default=None,
    help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 volumes"
    
    instances = filter_instances(project)

    for i in instances:
        
        for v in i.volumes.all():
            print(", ".join((
                v.id,
                i.id,
                str(v.size) + " GiB",
                v.state,
                str(v.create_time),
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))

    return

## Commands for Snapshots
@cli.group('snapshots')
def snapshots():
    """Commands for Snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
    help="Only snapshots for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
    help="List all snapshots for each volume, not just the most recent")
def list_snapshots(project, list_all):
    "List EC2 snapshots"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(', '.join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"),
                    str(s.description)
                )))

                if s.state == 'completed' and not list_all: break

    return


## Commands for Instances
@cli.group('instances')
def instances():
    """Commands for Instances"""

@instances.command('list')
@click.option('--project', default=None,
    help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"
    
    instances = filter_instances(project)

    for i in instances:
        tags = { t['Key']: t['Value'] for t in i.tags or [] }

        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
        )))

    return

@instances.command('start')
@click.option('--project', default=None,
    help="only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as ce:
            print(" Unable to start {0}.\n {1}".format((i.id), str(ce)))
            continue

    return

@instances.command('stop')
@click.option('--project', default=None,
    help="only instances for project (tag Project:<name>)")
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.exceptions.ClientError as ce:
            print(" Unable to stop {0}.\n {1}".format((i.id), str(ce)))
            continue


    return

@instances.command('terminate')
@click.option('--project', default=None,
    help="only instances for project (tag Project:<name>)")
def terminate_instances(project):
    "Terminate EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Terminating {0}...".format(i.id))
        i.terminate()

    return

@instances.command('snapshot')
@click.option('--project', default=None,
    help="only instances for project (tag Project:<name>)")
def snapshot_instances(project):
    "Snapshot EC2 Instance Volumes"

    instances = filter_instances(project)

    for i in instances:

        print("Stopping {0}...".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if has_pending_snapshot(v):
                print(" Skipping snapshot for {0}, snapshot in progress...".format(v.id))
                continue

            snapshot = v.create_snapshot(
                Description='Snapshot created by CloudSnap'
            )
            print("  Creating snapshot for volume {0}".format(v.id))
            print("  Snapshot ID: {0}".format(snapshot.id))

        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()

    return


## Main
if __name__ == '__main__':
    cli()    
    