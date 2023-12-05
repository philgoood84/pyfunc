"""
Useful decorators for the project
"""
from datetime import datetime
from typing import Callable
import functools
import time

def singleton(cls):
    """
    Make a class a Singleton class (only one instance)
    """
    @functools.wraps(cls)
    def wrapper_singleton(*args, **kwargs):
        if not wrapper_singleton.instance:
            wrapper_singleton.instance = cls(*args, **kwargs)
        return wrapper_singleton.instance
    wrapper_singleton.instance = None
    return wrapper_singleton

def disk_memoization(file: str, save_every: int = 1):
    def retrieve_cache_file(func):
        try:
            with open(file, 'rb') as f:
                cache = pickle.load(f)
        except:
            cache = {}
        unsaved = 0

        @functools.wraps(func)
        def with_cache(*args, **kwargs):
            try:
                key = hash((args, kwargs))
            except TypeError:
                key = repr((args, kwargs))
            try:
                value = cache[key]
            except KeyError:
                ret = cache[key] = fn(*args, **kwargs)
                unsaved += 1
                if unsaved >+ save_every:
                    with open(file, 'wb') as f:
                        pickle.dump(f)
                    unsaved = 0
            return ret

        return with_cache
    return retrieve_cache_file


def timeit(func):
    def wrappedf(*args, **kwargs):
        start = time.process_time()
        res = func(*args, **kwargs)
        end = time.process_time()
        print(f"{func.__name__} in {end - start}")
        return res
    return wrappedf

