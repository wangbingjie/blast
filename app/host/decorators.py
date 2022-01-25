import functools
from .models import ExternalResourceCall
import datetime


def save_external_resource_call(resource_name):
    """
    Decorator which saves metadata about a call to an external resource.
    """
    def decorator_save(func):
        @functools.wraps(func)
        def wrapper_save(*args, **kwargs):
            time_before = datetime.datetime.now()
            value = func(*args, **kwargs)
            time_after = datetime.datetime.now()
            call = ExternalResourceCall(resource_name=resource_name,
                                        time_called=time_before,
                                        )
            call.save()
            return value
        return wrapper_save
    return decorator_save