import dataclasses


@dataclasses.dataclass()
class Tunnel:
    """
    Base class for any port forwarding tunnel that can be made.
    """

    instance: str
    remote_port: int
    local_port: int = None
    local: bool = True
    address: str = '127.0.0.1'

    def __post_init__(self):
        self.validate()

    def validate(self):
        """
        Validate configuration of instance.
        """
        pass
