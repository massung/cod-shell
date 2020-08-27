# COD Shell

COD is a simple SSH CLI utility. It assists in saving SSH connection settings to an INI file so they can be loaded and connected to easily.

Additionally, it understands how to connect to AWS and other cloud-hosted servers by name so those don't have to be setup individually. This is especially helpful for things like AWS EMR job clusters where the instances are created on the fly and all you have handy is a cluster ID.

## Setup

Clone the repository from GitHub:

```bash
$ git clone https://github.com/massung/cod-shell.git
```

Change directories to the `cod-shell` directory and install it using setuptools:

```bash
$ python setup.py install
```

## Creating an SSH Connection

Once setup, you can add connections using `cod add` from the command line:

```bash
$ cod add my-server
host:
port [22]:
login [none]:
key [none]:
agent forwarding [false]:
```

The host name/IP is required, but all the others are optional. If no login is provided then you will be prompted for a username upon trying to connect. If no key is provided, then you will be prompted for a password as well.

_NOTE: The `key` should be a name and not a file as multiple hosts can all use the same key. When you attempt to connect to a server that requires a key COD doesn't know about, it will ask you to locate the SSH key (PEM file) on disk and will save a reference to it for future use._

## Connecting to a Server

Use the `cod sh` command to connect to a server you have set up:

```bash
$ cod sh my-server
```

At this point, if you specified a `key` name for the connection, COD will ask you to locate it for use. This will only happen once for each key.

## Connecting to a Cloud Instance

You don't need to `add` cloud servers. As long as you have the cloud service installed on your machine (e.g. `awscli` for AWS), you can just reference the cloud instance by name and provide a flag to COD indicating it is a cloud instance. For example:

```bash
$ cod sh my-ec2-instance --aws
```

This will tell COD that `my-ec2-instance` is an AWS instance. It will then connect to AWS using the credentials you have already configured on your machine to look up the instance name, get its IP address and any SSH key required to connect to it. To look up the instance, it first checks to see if the instance name is an instance id beginning with `i-` or a job flow ID beginning with `j-`. Otherwise it assumes the name provided matches the `Name` tag of the EC2 instance.

_NOTE: Right now there is only support for AWS, but GCP and Azure should be easy to add._
