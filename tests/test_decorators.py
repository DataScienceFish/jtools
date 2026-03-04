import sys
sys.path.append('F:/projects/jtools')

from jtools.decorators import retry, deprecated, retry_with_skip


def retry_if_zero_division_error(exception):
    return isinstance(exception, ZeroDivisionError)


@retry(stop_max_attempt_number=3, retry_on_exception=retry_if_zero_division_error)
def job1():
    a = 1/0
    return


# Examples
@deprecated(deprecated_in=0.1, removed_in=0.2, details="Already deprecated func")
def some_old_function(x, y):
    return x + y


class SomeClass:
    @deprecated(deprecated_in=0.1, removed_in=0.2, details="Already deprecated func")
    def some_old_method(self, x, y):
        return x + y


@retry_with_skip(max_attempts=3)
def divide_0():
    print(1/0)
    return True


def test_divide_0():
    some_old_function(1, 2)
    a = divide_0()
    return a


@deprecated(deprecated_in="1.0", removed_in="2.0",
            details="Use the bar function instead")
def test_foo():
    """Do some stuff"""
    print("Hello World")
    return 1


# test_foo()
