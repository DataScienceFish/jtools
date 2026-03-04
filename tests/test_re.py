import re


def replace_num(s):
    dict_num = {
        '0': '〇', 
        '1': '一', 
        '2': '二', 
        '3': '三', 
        '4': '四', 
        '5': '五', 
        '6': '六', 
        '7': '七', 
        '8': '八', 
        '9': '九'
    }
    # print(s.group())
    # print(s)
    return dict_num[s.group()]


def test_sub():
    my_str = '2018年6月7号'
    a = re.sub(r'(\d)', replace_num, my_str)
    print(a)  # 每次匹配一个数字，执行函数，获取替换后的值

    a = re.sub('(\d{4})-(\d{2})-(\d{2})', r'\2-\3-\1', '2018-06-07')
    print(a)
    a = re.sub('(\d{4})-(\d{2})-(\d{2})', r'\g<2>-\g<3>-\g<1>', '2018-06-07')
    print(a)


# pytest test_re.py -s
