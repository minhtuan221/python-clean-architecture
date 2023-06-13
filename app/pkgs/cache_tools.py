from functools import wraps


def cache(max_size=None):
    cache_dict = {}
    cache_order = []

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))

            if key in cache_dict:
                # Return cached result if available
                return cache_dict[key]

            # Call the function and cache the result
            result = func(*args, **kwargs)

            if max_size is not None and len(cache_order) >= max_size:
                # Remove the least recently used item if cache is full
                oldest_key = cache_order.pop(0)
                del cache_dict[oldest_key]

            cache_dict[key] = result
            cache_order.append(key)

            return result

        return wrapper

    return decorator
