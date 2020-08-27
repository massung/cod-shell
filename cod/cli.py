import botocore.errorfactory
import click
import logging
import os.path

from cod.aws import AWSInstance
from cod.config import Config
from cod.instance import BaseInstance
from cod.ssh import *
from cod.utils import *


@click.group()
def cli():
    pass


@click.command(name='add')
@click.argument('name')
@click.pass_obj
def cli_add(config, name):
    host = input(prompt='host: ')
    port = input(prompt='port [22]: ')
    login = input(prompt='login [none]: ')
    identity = input(prompt='key [none]: ')
    agent_forwarding = input(prompt='agent forwarding [false]: ')

    # create the instance
    instance = BaseInstance(
        host=host,
        port=int(port),
        login=login if login else None,
        identity=identity if identity else None,
        agent_forwarding=bool(agent_forwarding),
    )

    # add the instance to the configuration and save
    config.set_instance(name, instance)
    config.save()

    # success
    logging.info('Added %s to cod config.', name)


@click.command(name='rm')
@click.argument('name')
@click.pass_obj
def cli_rm(config, name):
    config.remove_instance(name)
    config.save()

    # success
    logging.info('Removed %s from cod config.', name)


@click.command(name='sh')
@click.argument('name')
@click.argument('command', nargs=-1)
@click.option('--aws', is_flag=True, help='host is an AWS EC2 or EMR cluster name')
@click.option('--login', '-l', help='username override')
@click.option('--port', '-p', type=int, help='port override')
@click.option('--identity', '-i', help='key override')
@click.pass_obj
def cli_sh(config, name, command, aws, login, port, identity):
    i = AWSInstance(config, name) if aws else config.instance(name)

    # ensure the instance exists
    assert i is not None, f'Unknown instance "{name}"; create with add command'

    # set the login and host address
    args = [f'{login or i.login}@{i.host}', '-p', str(port or i.port or 22)]

    # add the private key if needed
    if identity or i.identity:
        key_file = locate_private_key(config, identity or i.identity)

        # make sure the key file exists
        assert key_file and os.path.exists(key_file), f'Failed to locate private key "{i.identity}"'

        # add the key file to the command line
        args += ['-i', key_file]

        # add agent forwarding parameter
        if i.agent_forwarding:
            args.append('-A')

            # ensure that the agent service is running
            start_agent(config)
            add_agent_key(config, key_file)

    # execute the ssh command
    run_ssh(config, [*args, *command])


@click.command(name='tunnel')
@click.argument('name')
@click.pass_obj
def cli_tunnel(config, name):
    tunnel = config.tunnel(name)

    # ensure the instance exists
    assert tunnel is not None, f'Unknown tunnel "{name}"; create with add command'


# initialize the cli
cli.add_command(cli_add)
cli.add_command(cli_rm)
cli.add_command(cli_sh)
cli.add_command(cli_tunnel)


def main():
    """
    Entry point.
    """
    logging.basicConfig(level=logging.INFO, format='%(levelname)-5s - %(message)s')

    # disable info logging for 3rd party modules
    logging.getLogger('botocore').setLevel(logging.CRITICAL)
    logging.getLogger('boto3').setLevel(logging.CRITICAL)

    # load the global config file
    config = Config()

    try:
        cli(obj=config)
    except botocore.errorfactory.ClientError as e:
        logging.error('%s', str(e))
    except subprocess.CalledProcessError:
        logging.error('SSH command failed')
    except AssertionError as e:
        logging.error('%s', str(e))


if __name__ == '__main__':
    main()
