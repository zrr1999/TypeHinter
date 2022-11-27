#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2022/11/27 16:52
# @Author : Rongrui Zhan
# @desc : 本代码未经授权禁止商用
import re
import yaml
from tools.utils import replace_func, load_api_yaml

yaml_source_mapping = {
    "tools/yaml/ops.yaml": ["source/tensor/ops.py", "source/tensor/math.py"]
}
for yaml_path, source_paths in yaml_source_mapping.items():
    func_list = load_api_yaml(yaml_path)
    for source_path in source_paths:
        with open(source_path, 'r') as source:
            source = source.read()
        for func in func_list:
            source = replace_func(source, *func)
        with open(source_path.replace("source", "generated"), mode="w") as stub_file:
            stub_file.write(source)


# import paddle
#
# print(paddle.add().)
