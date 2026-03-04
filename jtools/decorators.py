import time
import functools
import traceback
from deprecation import deprecated
from retrying import retry


def func_timer(function):
    """
    计时装饰器
    :param function: 待计时函数
    :return: 函数结果
    """

    def function_timer(*args, **kwargs):
        print('[Function: {name} start...]'.format(name=function.__name__))
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print('[Function: {name} finished, spent time: {time:.3f}s]'.format(name=function.__name__, time=t1 - t0))
        return result

    return function_timer


# @deprecated(deprecated_in=0.1, details="using retry instead")
@retry(stop_max_attempt_number=3)
def error_handler(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except:
            msg = traceback.format_exc()
            print(msg)
            return -1
    return wrapper


def retry_with_skip(max_attempts=3, retry_interval=1000, default_return=None):
    """
    自定义装饰器，封装重试逻辑，并在重试失败后跳过。

    :param max_attempts: 最大重试次数
    :param retry_interval: 重试间隔（毫秒）
    :param default_return： 报错后默认返回
    """
    def decorator(func):
        @functools.wraps(func)
        @retry(stop_max_attempt_number=max_attempts,
               wait_fixed=retry_interval)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # print(f"重试 {max_attempts} 次后失败，跳过。异常信息：{e}")
                traceback.print_exc()
                return default_return  # 或者返回其他默认值或执行其他操作
        return wrapper

    return decorator


# def continue_run(n=99999, finish_msg='All tasks finished', error_msg='Error occur {}', stop_msg='Stop for state {}'):
#     """
#     continue runner with mailing system, only support 3 states: 0:finish, -1:error, 1:stop
#     :param n:
#     :param finish_msg:
#     :param error_msg:
#     :param stop_msg:
#     :return:
#     """
#     def decorate(func):
#         @functools.wraps(func)
#         def wrapper(*args, **kwargs):
#             # i = 0
#             # error_count = 0
#             # subject = f"Function {__file__.split('/')[-1]}-{func.__name__}"
#             while True:
#                 try:
#                     state = func(*args, **kwargs)
#                     if state == 0:
#                         send_mail(stop_msg.format(state), subject)
#                         break
#                     elif state == -1:
#                         send_mail(error_msg.format(state), subject)
#                         break
#                     elif state == 1:
#                         send_mail(finish_msg, subject)
#                         break
#                 except Exception as e:
#                     msg = traceback.format_exc()
#                     logging.error(msg)
#                     time.sleep(1)
#                     state = -99
#                     # send_mail(error_msg.format(e), subject)
#                     continue
#                 finally:
#                     i += 1
#                     if i >= n:
#                         break
#             return state
#         return wrapper
#     return decorate
