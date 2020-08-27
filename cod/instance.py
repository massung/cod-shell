import dataclasses


@dataclasses.dataclass()
class BaseInstance:
    """
    Base class for any machine instance that can be connected to.
    """

    host: str
    port: int = 22
    login: str = None
    identity: str = None
    agent_forwarding: bool = False

    def __post_init__(self):
        self.validate()

    def validate(self):
        """
        Validate configuration of instance.
        """
        assert self.host, 'Instance has no public IP address'

        if self.agent_forwarding:
            assert self.identity, 'Cannot forward agent without an identity'

    @property
    def ssh_command(self):
        """
        """
