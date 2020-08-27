import easygui
import os
import os.path
import subprocess

from cod.utils import *


def run_ssh(config, args, shell=False):
    """
    Run the command line options in command.
    """
    ssh = config.get('ssh') or 'ssh'
    command = [ssh, *args]

    # execute the command, wait for it to complete
    process = subprocess.run(command, env=os.environ, shell=shell)
    process.check_returncode()

    # no assertion tripped, assume success, write out the config
    config.save()


def start_agent(config):
    """
    Ensure that ssh-agent is running.
    """
    ssh_agent = config.get('ssh-agent') or 'ssh-agent'

    # this just starts the service running if it wasn't already
    process = subprocess.run([ssh_agent], env=os.environ)
    process.check_returncode()


def add_agent_key(config, key_file):
    """
    Add an SSH key to the agent for agent forwarding.
    """
    ssh_add = config.get('ssh-add') or 'ssh-add'

    # add the key
    process = subprocess.run([ssh_add, '-q', key_file], env=os.environ)
    process.check_returncode()


def locate_private_key(config, identity):
    """
    Lookup where the private key is on disk from the config or
    prompt the user to locate it.
    """
    title = 'Locate private key'

    if identity is not None:
        title += f' "{identity}"'

    # find the key in the config or locate it
    key_file = (identity and config.identity(identity)) or easygui.fileopenbox(title=title)

    # write the location of the key file back to the config
    if key_file is not None:
        if identity is None:
            identity = cap_case_filename(key_file)

        # add the name to the config file
        config.set_identity(identity, key_file)

    return key_file
