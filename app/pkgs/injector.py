import inspect
from functools import wraps
from typing import Callable, get_type_hints, Dict


class Container(object):

    def __init__(self):
        self.map_instance = {}

    def inject(self, cls):
        if not inspect.isclass(cls):
            return cls
        sign = inspect.signature(cls)
        parameter: Dict[str, inspect.Parameter] = sign.parameters
        prepared_input = dict()
        for k, p in parameter.items():
            dependence_name = p.annotation.__name__
            dependence_instance = self.map_instance.get(dependence_name, None)
            if isinstance(dependence_instance, p.annotation):
                prepared_input[k] = dependence_instance
        return cls(**prepared_input)

    def auto_inject(self, cls):
        if not inspect.isclass(cls):
            return cls
        if cls.__name__ in self.map_instance:
            return self.map_instance
        class_instance = self.inject(cls)
        self.map_instance[cls.__name__] = class_instance
        return class_instance

    def add_singleton(self, cls, *args, **kwargs):
        if inspect.isclass(cls):
            c = cls(*args, **kwargs)
            name = cls.__name__
        else:
            name = type(cls).__name__
            c = cls
        if name not in self.map_instance:
            self.map_instance[name] = c
        return self.map_instance[name]

    def get_singleton(self, cls):
        if inspect.isclass(cls):
            name = cls.__name__
        else:
            name = type(cls).__name__
        return self.map_instance.get(name, None)

