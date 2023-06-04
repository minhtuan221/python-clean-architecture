import inspect
import typing as t

D = t.TypeVar('D')  # dependency


class Container(object):

    def __init__(self):
        self.map_class = {}
        self.map_instance = {}
        self.last_error = None

    def get_class_name(self, dependency) -> str:
        if self.is_primal_type(dependency):
            return ''
        if inspect.isclass(dependency):
            return dependency.__name__
        return type(dependency).__name__

    def is_primal_type(self, p) -> bool:
        if p in (bool, int, str, float, list, dict, tuple, set):
            return True
        if isinstance(p, (bool, int, str, float, list, dict, tuple, set)):
            return True
        return False

    def inject(self, dependency: t.Type[D]) -> t.Optional[D]:
        if not inspect.isclass(dependency):
            return dependency
        parameter: t.Mapping[str, inspect.Parameter] = inspect.signature(dependency).parameters
        prepared_input = dict()
        for k, p in parameter.items():
            dependence_name = self.get_class_name(p.annotation)
            dependence_instance = self.map_instance.get(dependence_name or k, None)
            if isinstance(dependence_instance, p.annotation):
                prepared_input[k] = dependence_instance
        try:
            return dependency(**prepared_input)
        except TypeError as e:
            self.last_error = ValueError(f"{dependency.__name__} error: {str(e)}")
            return None

    def auto_inject(self, dependency: t.Type[D]) -> t.Optional[D]:
        """try to create instance of dependency. If not successful, return None
        """
        if not inspect.isclass(dependency):
            raise ValueError(f'auto inject receive class only but receive {dependency}, type is {type(dependency)}')
        if dependency.__name__ in self.map_instance:
            return self.map_instance
        class_instance = self.inject(dependency)
        if not class_instance:
            return None
        self.map_instance[dependency.__name__] = class_instance
        return class_instance

    def add_instance(self, dependency_instance: D, name: str = '') -> D:
        """create and add instance directly, is used by add config also"""
        if not name:
            name = type(dependency_instance).__name__
        elif not self.is_primal_type(dependency_instance):
            raise ValueError(f'add_instance receive class type with empty name but receive {name}')
        if name in self.map_instance:
            raise ValueError(f'name ({name}) already in map_instance')

        self.map_instance[name] = dependency_instance
        self.map_class[name] = '' if self.is_primal_type(dependency_instance) else type(dependency_instance)
        return self.map_instance[name]

    def add_config(self, name: str, value: D) -> D:
        return self.add_instance(value, name=name)

    def add_singleton(self, dependency: t.Type[D]):
        # add class type to map
        if not inspect.isclass(dependency):
            raise ValueError(f"add_singleton receive class only, but receive {dependency}")
        self.map_class[dependency.__name__] = dependency

    def get_singleton(self, dependency: t.Type[D]) -> D:
        if inspect.isclass(dependency):
            name = dependency.__name__
        else:
            name = type(dependency).__name__
        return self.map_instance.get(name, None)

    def build(self, max_round=10) -> int:
        i = 0
        while i < max_round:
            if len(self.map_class) == len(self.map_instance):
                # all class is created
                break
            for k, dependency in self.map_class.items():
                # dependency = '' if it's config
                if dependency:
                    self.auto_inject(dependency)
            i += 1
        if len(self.map_class) != len(self.map_instance):
            if self.last_error:
                raise self.last_error
            else:
                raise ValueError('cannot create all instance')
        return i


