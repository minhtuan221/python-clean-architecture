import time
from functools import wraps

import pytest


class Cache:
    def __init__(self, max_size=None, expire_time=None):
        self.max_size = max_size
        self.expire_time = expire_time  # seconds
        self.cache_dict = {}
        self.cache_order = {}

    def __call__(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(kwargs.items()))

            if key in self.cache_dict:
                # Check if the cache has expired
                if self.expire_time is not None:
                    cached_time = self.cache_order[key]
                    current_time = time.time()
                    if current_time - cached_time > self.expire_time:
                        # Remove the expired cache entry
                        del self.cache_dict[key]
                        del self.cache_order[key]
                else:
                    # Return cached result if available
                    return self.cache_dict[key]

            # Call the function and cache the result
            result = func(*args, **kwargs)

            if self.max_size is not None and len(self.cache_order) >= self.max_size:
                # Remove the least recently used item if cache is full
                oldest_key = min(self.cache_order, key=self.cache_order.get)
                del self.cache_dict[oldest_key]
                del self.cache_order[oldest_key]

            self.cache_dict[key] = result
            self.cache_order[key] = time.time()

            return result

        return wrapper


cache = Cache(max_size=1000, expire_time=120)

# Define a test function
def expensive_function(n):
    # Simulate an expensive computation
    time.sleep(1)
    return n


# Create an instance of the Cache decorator with a max size of 5 and expire time of 2 seconds
cache_decorator = Cache(max_size=5, expire_time=2)


# Define a test case for caching the expensive_function
def test_cache_decorator():
    # Apply the cache decorator to the expensive_function
    cached_function = cache_decorator(expensive_function)

    # Call the cached function multiple times with the same argument
    result1 = cached_function(5)
    result2 = cached_function(5)
    result3 = cached_function(5)

    # Ensure that the function is only called once
    assert expensive_function.call_count == 1

    # Ensure that the results are cached and equal
    assert result1 == result2 == result3

    # Call the function with a different argument
    result4 = cached_function(10)

    # Ensure that the function is called again for the new argument
    assert expensive_function.call_count == 2

    # Ensure that the results are different for the new argument
    assert result4 != result1

    # Wait for the cache to expire
    time.sleep(3)

    # Call the function again with the same argument
    result5 = cached_function(5)

    # Ensure that the function is called again after cache expiration
    assert expensive_function.call_count == 3

    # Ensure that the new result is different from the previous cached result
    assert result5 != result1


# Run the tests using pytest
# pytest.main([__file__])
