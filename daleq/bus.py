from daleq.device import Device, Version


class Bus(Device):
    def __init__(self, id: str):
        super().__init__(id)
        self.children = []

    def setup(self):
        pass

    def version(self) -> Version:
        return Version(0, 1)

    def type(self) -> str:
        return 'bus'

    def add(self, device: Device):
        if device.parent is not None:
            raise "Device already added to a bus"

        if device not in self.children:
            self.children.append(device)
            device.parent = self

    def handle(self, target: list, msg):
        result = dict()

        # Breadth first
        result[self.id] = super().handle(target, msg)

        # Propagate message on to children
        if not target or target[0] == self.id:
            new_target = target[1:]
            for child in self.children:
                result[child.id] = child.handle(new_target, msg)

        return result

