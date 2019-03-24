import itertools
import time


def retry(delays=(0, 1, 5, 30, 180, 600, 3600), exception=Exception):
    """
    Decorator which performs retries with dynamic intervals set by given delays tuple. Also pulls
    report kwarg from the wrapped function call for logging.
    :param delays: tuple of wait time (seconds)
    :type delays: tuple
    :param exception: what exception to catch for retries
    :type exception: type
    :return: wrapped function
    :rtype: function
    """

    def wrapper(func):
        def wrapped(*args, **kwargs):
            report = kwargs['report']
            problems = []
            for delay in itertools.chain(delays, [None]):
                try:
                    return func(*args, **kwargs)
                except exception as problem:
                    problems.append(problem)
                    if delay is None:
                        report("Retryable failed definitely:", problems)
                        raise
                    else:
                        report("Retryable failed:", problem, "-- delaying for %ds" % delay)
                        time.sleep(delay)

        return wrapped
    return wrapper
