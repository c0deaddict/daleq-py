from abc import ABC, abstractmethod
from enum import Enum
from daleq.persistence import Store


class PropertyAccess(Enum):
    READ_ONLY = 'r'
    READ_WRITE = 'rw'
    WRITE_ONLY = 'w'

    def can_read(self):
        return 'r' in self.value

    def can_write(self):
        return 'w' in self.value


class PropertyDefinition(object):
    def __init__(self, access: PropertyAccess, persistent: bool):
        self.access = access
        self.persistent = persistent

    def to_json(self) -> dict:
        return {
            'access': self.access.value,
            'persistent': self.persistent
        }


class Version(object):
    def __init__(self, major: int, minor: int):
        self.major = major
        self.minor = minor


class Device(ABC):
    def __init__(self, id, store: Store = None):
        self.id = id
        self.store = store
        self.parent = None
        self.enabled = True
        self.labels = dict()
        self.property_definitions = {
            'enabled': PropertyDefinition(PropertyAccess.READ_WRITE, self.is_persistent())
        }

    @abstractmethod
    def type(self) -> str:
        pass

    @abstractmethod
    def version(self) -> Version:
        pass

    @abstractmethod
    def setup(self):
        pass

    def fqid(self):
        parent_fqid = self.parent.fqid() if self.parent is not None else []
        return parent_fqid + [self.id]

    def is_persistent(self):
        return self.store is not None

    def get_enabled(self) -> bool:
        return self.enabled

    def set_enabled(self, value: bool):
        self.enabled = value
        return True

    def get(self, key, persistent):
        """
        Get the value of a property. The persistent flag determines from which store the
        value comes: either from transient (persistent=false) or persistent (if it is available).
        :param key: Property key
        :param persistent: Boolean flag to indicate the store
        :return: Value or None if not found or something went wrong
        """
        p = self.property_definitions.get(key)
        if p is not None and p.access.can_read():
            if not persistent:
                return getattr(self, 'get_' + key)()
            elif self.is_persistent():
                return self.store.get(self.fqid(), key)
        return None

    def set(self, key, value, persistent) -> bool:
        """
        Set the value of a property. Just like get, the value of persistent determines the store.
        :param key: Property key
        :param value: New value
        :param persistent: Boolean flag to indicate the store
        :return: True if succeeded, False if failed
        """
        p = self.property_defintions.get(key)
        if p is not None and p.access.can_write():
            if not persistent:
                return getattr(self, 'set_' + key)(value)
            elif self.is_persistent():
                return self.store.set(self.fqid(), key)

        return False

    def handle(self, target: list, msg):
        """
        Handle a message (from MQTT)
        :param target: Target path
        :param msg: Json message
        """
        if not target or target == [self.id]:
            if isinstance(msg, dict):
                if 'describe' in msg:
                    return self.handle_describe(msg.get('describe'))
                elif 'get' in msg:
                    return self.handle_get(msg.get('get'))
                elif 'set' in msg:
                    return self.handle_set(msg.get('set'))
                else:
                    return self.handle_other(msg)

        return None

    def handle_other(self, msg):
        return None

    def handle_describe(self, msg):
        return {
            'id': self.id,
            'type': self.type(),
            'labels': self.labels,
            'properties': {k: v.to_json() for (k, v) in self.property_definitions}
        }

    def handle_get(self, msg):
        if isinstance(msg, str):
            return self.get(msg, False)
        elif isinstance(msg, dict):
            key = msg.get('key')
            persistent = msg.get('persistent', False)
            return self.get(key, persistent)

    def handle_set(self, msg):
        if isinstance(msg, dict):
            key = msg.get('key')
            value = msg.get('value')
            persistent = msg.get('persistent', False)
            return self.set(key, value, persistent)


class Sensor(Device):
    def __init__(self, id: str):
        super().__init__(id)

    @abstractmethod
    def read(self):
        pass


class Actuator(Device):
    def __init__(self, id):
        super().__init__(id)

    @abstractmethod
    def execute(self, cmd):
        pass

