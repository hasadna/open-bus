import itertools
import logging
import time


def retry(delays=(0, 1, 5, 30, 180, 600, 3600), exception=Exception):
    """
    Decorator which performs retries with dynamic intervals set by given delays tuple.
    :param delays: tuple of wait time (seconds)
    :type delays: tuple
    :param exception: what exception to catch for retries
    :type exception: type
    :return: wrapped function
    :rtype: function
    """

    def wrapper(func):
        def wrapped(*args, **kwargs):
            problems = []
            for delay in itertools.chain(delays, [None]):
                try:
                    return func(*args, **kwargs)
                except exception as problem:
                    problems.append(problem)
                    if delay is None:
                        logging.error("Retryable failed definitely:", problems)
                        raise
                    else:
                        logging.error("Retryable failed:", problem, "-- delaying for %ds" % delay)
                        time.sleep(delay)

        return wrapped
    return wrapper
