import inspect
import typing as t

import pytest as pytest

D = t.TypeVar('D')  # dependency


class Container(object):

    def __init__(self):
        self.map_class = {}
        self.map_instance = {}
        self.last_error = None

    def get_class_name(self, dependency) -> str:
        if dependency in (bool, int, str, float, list, dict, tuple, set):
            return ''
        if isinstance(dependency, (bool, int, str, float, list, dict, tuple, set)):
            return ''
        if inspect.isclass(dependency):
            return dependency.__name__
        return type(dependency).__name__

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
            raise ValueError('auto inject receive class only, not instance')
        if dependency.__name__ in self.map_instance:
            return self.map_instance
        class_instance = self.inject(dependency)
        if not class_instance:
            return None
        self.map_instance[dependency.__name__] = class_instance
        return class_instance

    def add_instance(self, dependency_instance: D, name: str = ''):
        """create and add instance directly, is used by add config also"""
        if not name:
            name = type(dependency_instance).__name__
        if name in self.map_instance:
            raise ValueError(f'name ({name}) already in map_instance')

        self.map_instance[name] = dependency_instance
        self.map_class[name] = self.get_class_name(dependency_instance)
        return self.map_instance[name]

    def add_config(self, name: str, value):
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

    def build(self, max_round=10):
        i = 0
        while i < max_round:
            if len(self.map_class) == len(self.map_instance):
                # all class is created
                break
            for dependency in self.map_class.values():
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


class RepoA:

    def __init__(self, config: str):
        self.config = config


class RepoB:
    def __init__(self, product_type: str = 'default'):
        self.product_type = product_type


class ServiceA:
    def __init__(self, repo_a: RepoA):
        self.repo_a = repo_a

    def config(self):
        return self.repo_a.config


class ServiceAB:
    def __init__(self, repo_a: RepoA, repo_b: RepoB):
        self.repo_a = repo_a
        self.repo_b = repo_b

    def config(self):
        return self.repo_a.config

    def product_type(self):
        return self.repo_b.product_type


class UseCaseAB:

    def __init__(self, service_a: ServiceA, service_ab: ServiceAB, product: str = 'product'):
        self.service_a = service_a
        self.service_ab = service_ab
        self.product = product


class TestContainer:

    @pytest.fixture
    def container(self):
        return Container()

    def test_create_2_layer_instances(self, container):
        container.add_singleton(ServiceA)
        container.add_singleton(RepoA)
        container.add_config('config', 'test.db')
        container.build()
        repo_a = container.get_singleton(RepoA)
        assert repo_a.config == 'test.db'
        assert container.get_singleton(ServiceA).config() == 'test.db'

    def test_create_2_layer_instances_with_default_config(self, container):
        container.add_singleton(ServiceAB)
        container.add_singleton(RepoA)
        container.add_singleton(RepoB)
        container.add_config('config', 'test.db')
        container.build()
        repo_a = container.get_singleton(RepoA)
        assert repo_a.config == 'test.db'
        assert container.get_singleton(ServiceAB).config() == 'test.db'
        assert container.get_singleton(ServiceAB).product_type() == 'default'

    def test_create_3_layer_instances(self, container):
        container.add_singleton(UseCaseAB)
        container.add_singleton(ServiceA)
        container.add_singleton(ServiceAB)
        container.add_singleton(RepoA)
        container.add_singleton(RepoB)
        container.add_config('config', 'test.db')
        container.build()
        repo_a = container.get_singleton(RepoA)
        assert repo_a.config == 'test.db'
        assert container.get_singleton(ServiceAB).config() == 'test.db'
        assert container.get_singleton(ServiceAB).product_type() == 'default'
        assert container.get_singleton(UseCaseAB).service_a == container.get_singleton(ServiceA)
        assert container.get_singleton(UseCaseAB).service_ab == container.get_singleton(ServiceAB)
        assert container.get_singleton(UseCaseAB).product == 'product'

    def test_create_instance_with_missing_dependency(self, container):
        container.add_singleton(ServiceA)
        container.add_singleton(RepoA)
        container.add_config('config', 'test.db')
        container.add_singleton(ServiceAB)

        with pytest.raises(ValueError):
            # The RepoB dependency is missing, which should raise an exception
            container.build()

    def test_create_instance_with_missing_config(self, container):
        container.add_singleton(ServiceA)
        container.add_singleton(RepoA)

        with pytest.raises(ValueError):
            # The config of repo A is missing, which should raise an exception
            container.build()

    def test_create_instance_with_max_rounds_reached(self, container):
        container.add_singleton(ServiceA)
        container.add_singleton(RepoA)
        container.add_config('config', 'test.db')

        # Setting max_rounds to 0 to force an endless loop
        with pytest.raises(ValueError):
            # Max rounds is reached without resolving all dependencies, which should raise an exception
            container.build(max_round=0)
