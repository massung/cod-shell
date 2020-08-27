import configparser
import dataclasses
import logging
import pathlib

from cod.instance import BaseInstance
from cod.tunnel import Tunnel


class Config:
    """
    Loads the "~/cod.ini" configuration file into memory. It is an INI file
    with the following sections:

    # global settings here
    ssh=/usr/bin/ssh
    ssh-agent=/usr/bin/ssh-agent
    ssh-add=/usr/bin/ssh-add

    [aws]
    aws_access_key_id=
    aws_secret_access_key=

    [keys]
    my-key=/home/me/.ssh/some_key

    [instance.<name>]
    host=
    port=
    login=
    identity=
    agent_forwarding=

    [tunnel.<name>]
    instance=
    address=
    remote_port=
    local_port=
    local=
    """

    def __init__(self, dot_file=None):
        """
        Load the dot file and parse it.
        """
        self.dot_file = dot_file

        # default to ~/ezsh.ini
        if not self.dot_file:
            self.dot_file = str(pathlib.Path.home().joinpath('cod.ini'))

        try:
            # attempt to read the dot file as an INI
            self.config = configparser.ConfigParser()
            self.config.read(self.dot_file)
        except OSError as e:
            logging.warning('%s does not exist; creating...', self.dot_file)
        except configparser.Error as e:
            logging.error('Failed to load %s; %s', self.dot_file, e)

    def save(self):
        """
        Write the configuration file.
        """
        try:
            with open(self.dot_file, mode='wt') as fp:
                self.config.write(fp)
        except OSError as e:
            logging.error('Failed to save %s; %s', self.dot_file, e)

    def get(self, option, default=None):
        """
        Lookup a global option value in the DEFAULT section.
        """
        return self.config.get('DEFAULT', option, fallback=default)

    def set(self, option, value):
        """
        Set a global option value.
        """
        if not self.config.has_section('DEFAULT'):
            self.config.add_section('DEFAULT')
        self.config.set('DEFAULT', option, str(value))

    def identity(self, name):
        """
        Return the settings for a saved SSH key.
        """
        if not self.config.has_section('keys'):
            return None
        return self.config.get('keys', name, fallback=None)

    def set_identity(self, name, value):
        """
        Write the key name and save the configuration.
        """
        if not self.config.has_section('keys'):
            self.config.add_section('keys')
        self.config.set('keys', name, str(value))

    def section(self, name, dataclass_constructor):
        """
        Lookup a section and return an instance of it.
        """
        if self.config.has_section(name):
            return dataclass_constructor(**dict(self.config.items(name)))

    def set_section(self, name, dataclass_instance):
        """
        Overwrite a section in the configuration.
        """
        if not self.config.has_section(name):
            self.config.add_section(name)

        # add/update the options
        for k, v in dataclasses.asdict(dataclass_instance).items():
            if v is not None:
                self.config.set(name, k, str(v))

    def remove_section(self, name):
        """
        Remove a section from the configuration.
        """
        if self.config.has_section(name):
            self.config.remove_section(name)

    def tunnel(self, name):
        """
        Return the settings for a tunnel.
        """
        return self.section(f'tunnel.{name}', Tunnel)

    def set_tunnel(self, name, tunnel):
        """
        Update the parameters of a tunnel entry.
        """
        self.set_section(f'instance.{name}', tunnel)

    def remove_tunnel(self, name):
        """
        Remove an instance section.
        """
        self.remove_section(f'tunnel.{name}')

    def instance(self, name):
        """
        Return the details of a particular instance as a dictionary. If
        the instance doesn't exist, returns None.
        """
        return self.section(f'instance.{name}', BaseInstance)

    def set_instance(self, name, instance):
        """
        Overwrite the instance section for a particular instance with
        an updated BaseInstance connection settings.
        """
        self.set_section(f'instance.{name}', instance)

    def remove_instance(self, name):
        """
        Remove an instance section.
        """
        self.remove_section(f'instance.{name}')
