import boto3
import re

from cod.instance import BaseInstance


class AWSInstance(BaseInstance):
    """
    EC2 instance description from AWS.
    """

    def __init__(self, config, id_or_name):
        """
        Use the AWS EC2 client to look up an instance by ID or name.
        """
        session = boto3.session.Session(
            aws_access_key_id=config.get('aws_access_key_id'),
            aws_secret_access_key=config.get('aws_secret_access_key'),
        )

        # ec2 connection settings
        ec2_client = session.client('ec2')
        login = 'ec2-user'

        # is this an emr cluster id?
        if _is_cluster_id(id_or_name):
            emr_client = session.client('emr')
            login = 'hadoop'

            # get the master ec2 instance if a cluster
            resp = emr_client.list_instances(
                ClusterId=id_or_name,
                InstanceGroupTypes=['MASTER'],
                InstanceStates=['RUNNING'],
            )

            # get the only master instance
            instances = resp and resp['Instances']

            # make sure a running instance exists
            assert instances, f'No instances found for cluster {id_or_name}'

            # only care about a master node
            id_or_name = instances[0]['Ec2InstanceId']

        # arguments to access instance
        kwargs = {}

        # filters based on the instance parameter
        if _is_instance_id(id_or_name):
            kwargs['InstanceIds'] = [id_or_name]
        else:
            kwargs['Filters'] = [
                {'Name': 'tag:Name', 'Values': [id_or_name]}
            ]

        # issue the aws request
        resp = ec2_client.describe_instances(**kwargs)
        instance = resp and _get_instance(resp)

        # assert it exists
        assert instance, f'Instance {id_or_name} not found or is ambiguous'

        # assert the instance is running
        assert instance.get('State', {}).get('Name') == 'running', f'Instance {id_or_name} is not running'

        # initialize the base instance dataclass
        super().__init__(
            host=instance.get('PublicIpAddress'),
            identity=instance.get('KeyName'),
            login=login,
        )


def _is_cluster_id(s):
    """
    True if `s` matches an EMR job-flow ID.
    """
    return re.match(r'j-[0-9a-z]+', s, re.IGNORECASE) is not None


def _is_instance_id(s):
    """
    True if `s` matches an EC2 instance ID.
    """
    return re.match(r'i-[0-9a-f]+', s, re.IGNORECASE) is not None


def _get_instance(resp):
    """
    Get the one and only match for the instance list in the response. If
    there are more or less and one match, log errors and return None.
    """
    instances = [i for r in resp['Reservations'] for i in r['Instances']]

    # return the one and only match
    if len(instances) == 1:
        return instances[0]
