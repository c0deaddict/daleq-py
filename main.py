from daleq.bus import Bus
from daleq.device import Sensor, Version
from daleq.node import Node


class NoDevice(Sensor):
    def setup(self):
        pass

    def version(self) -> Version:
        return Version(0, 1)

    def type(self) -> str:
        return 'noop'

    def read(self):
        return 'test'


if __name__ == '__main__':
    n = Node('fractal', '10.13.37.2')
    n.add(NoDevice('d1'))
    n.add(NoDevice('d2'))
    b1 = Bus('bus1')
    b1.add(NoDevice('d3'))
    n.add(b1)
    b2 = Bus('bus2')
    b2.add(NoDevice('d4'))
    b1.add(b2)
    n.client.loop_forever()
