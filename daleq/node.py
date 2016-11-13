import json
from daleq.bus import Bus
import paho.mqtt.client as mqtt

from daleq.device import Version


def split(lst: list, i: int) -> (list, list):
    """
    Split a list into two sub lists at a fixed position

    >>> split([1,2,3], 2)
    ([1, 2], [3])
    >>> split([1,2], 3)
    ([1, 2], [])
    >>> split([1], 1)
    ([1], [])

    :param lst: Input list
    :param i: Start position of the second sub list
              Also the length of the first sub list
    :return: Tuple of first and second sub list
    """
    return lst[0:i], lst[i:]


class Node(Bus):
    TOPIC_ROOT = ['dev']
    TOPIC_SEPARATOR = '/'
    TOPIC_REGISTER = 'register'
    TOPIC_UNREGISTER = 'unregister'
    TOPIC_REQUEST = 'request'
    TOPIC_UPDATE = 'update'

    def __init__(self, id: str, host: str, port: int = 1883, userdata=None):
        super().__init__(id)
        self.client = mqtt.Client(id, userdata=userdata)
        self.client.on_connect = lambda client, userdata, flags, rc: self.on_connect(flags, rc)
        self.client.on_message = lambda client, userdata, msg: self.on_message(msg)
        self.client.connect(host, port)

    def type(self) -> str:
        return 'node'

    def version(self) -> Version:
        return Version(0, 1)

    def setup(self):
        pass

    @staticmethod
    def make_topic(*args):
        """
        >>> Node.make_topic('a', 'b', 'c')
        'dev/a/b/c'
        """
        path = (Node.TOPIC_ROOT + list(args))
        return Node.TOPIC_SEPARATOR.join(path)

    def on_connect(self, flags, rc):
        print('connected! flags=%s rc=%d' % (flags, rc))
        self.client.subscribe(self.make_topic(self.TOPIC_REQUEST, '#'))
        self.client.subscribe(self.make_topic(self.TOPIC_UPDATE, '#'))

    def on_message(self, msg: mqtt.MQTTMessage):
        try:
            path = msg.topic.split(Node.TOPIC_SEPARATOR)
            expect_prefix = Node.TOPIC_ROOT + [Node.TOPIC_REQUEST]
            prefix, rest = split(path, len(expect_prefix))
            if prefix == expect_prefix:
                obj = json.loads(msg.payload.decode('utf-8').rstrip('\x00'))
                print(self.handle(rest, obj))
        except Exception as e:
            raise e
            #print(e)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
