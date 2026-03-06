from typing import Union, Dict, List
import json


def save_to_json(filepath: str, datas: Union[Dict, List[Dict]], mode='a+', encoding='utf-8-sig', ensure_ascii=False, **kwargs) -> int:
    """(add) save datas to .json file

    :param filepath: file path
    :param datas: data objects
    :param mode: write mode, default a+ for adding
    :param encoding: encoding of file content
    :return: counts of datas
    """
    if isinstance(datas, dict):
        datas = [datas]
    _lines = [json.dumps(data, ensure_ascii=ensure_ascii, **kwargs) for data in datas]
    with open(filepath, mode=mode, encoding=encoding) as _f:
        _f.writelines("\n".join(_lines))
        _f.write('\n')
    return len(_lines)
