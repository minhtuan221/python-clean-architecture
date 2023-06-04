import pytest as pytest

from app.pkgs.injector import Container


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

    def test_add_non_primal_config(self, container):
        container.add_singleton(ServiceA)

        with pytest.raises(ValueError):
            container.add_config('repo_a', RepoA('abc'))
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
