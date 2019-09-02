from functools import wraps
from inspect import getfullargspec
from typing import get_type_hints, Any


def check_origin_type(result, requirement):
    if str(requirement).startswith('typing.List'):
        return isinstance(result, list)
    if str(requirement).startswith('typing.Dict'):
        return isinstance(result, dict)
    return isinstance(result, requirement)


def match_return(all_required, all_results):
    if len(all_required) != len(all_results):
        # raise error if number of requirements and return is not match
        raise TypeError(
            f'Number of return Argument and required is not match: require {len(all_required)} value, received {len(all_results)} value')
    for requirements, result in zip(all_required, all_results):
        # print(requirements, result)
        if requirements is None:
            if result is not None:
                raise TypeError(
                    'Return value %r is not of type %s' % (
                        result, requirements)
                )
        elif requirements != Any and not check_origin_type(result, requirements):
            # print(requirements, result)
            raise TypeError(
                'Return value %r is not of type %s' % (
                    result, requirements)
            )


def validate_input(func, **kwargs):
    hints = get_type_hints(func)
    # print(hints)
    # get all type of result function
    all_results = func(**kwargs)
    all_results = (all_results,)

    # print('all_results', all_results)
    # iterate all type hints
    for attr_name, attr_type in hints.items():
        if attr_name == 'return':
            # get all type of requirement
            all_required = hints['return']
            all_required = (all_required,)
            match_return(all_required, all_results)
        elif attr_type != Any and not check_origin_type(kwargs[attr_name], attr_type):
            raise TypeError(
                'Argument %r = %r is not of type %s' % (
                    attr_name, kwargs[attr_name], attr_type)
            )
    if len(all_results) == 1:
        return all_results[0]
    else:
        return all_results


def type_check(decorator):
    """Function check all type of input argument and return value of 'def' as specified in typing module (from python 3.3).
    It will raise Type Error if any wrong type. Cannot work correctly with List[object], Dict[object], Tuple, ...

    Arguments:
        decorator {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    @wraps(decorator)
    def wrapped_decorator(*args, **kwargs):
        # translate *args into **kwargs
        func_args = getfullargspec(decorator)[0]
        default_kwargs = getfullargspec(decorator).defaults or []
        kwargs.update(dict(zip(func_args, args)))
        # update default value
        func_defaults = [arg for arg in func_args if arg not in kwargs]
        # print('func_args=', func_args, 'kwargs=', kwargs)
        # print('func_defaults=', func_defaults,
        #   'default_kwargs=', default_kwargs)
        kwargs.update(dict(zip(func_defaults, default_kwargs)))
        return validate_input(decorator, **kwargs)

    return wrapped_decorator
