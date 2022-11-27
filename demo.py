#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2022/11/27 16:52
# @Author : Rongrui Zhan
# @desc : 本代码未经授权禁止商用
import os
from tools.utils import replace_func, load_api_yaml

yaml_paths = ['tools/yaml/strings_ops.yaml', 'tools/yaml/sparse_backward.yaml',
              'tools/yaml/backward.yaml', 'tools/yaml/sparse_ops.yaml',
              'tools/yaml/legacy_ops.yaml', 'tools/yaml/legacy_backward.yaml', 'tools/yaml/ops.yaml']
func_list = []
for yaml_path in yaml_paths:
    func_list.extend(load_api_yaml(yaml_path))

source_paths = ['source/tensor/manipulation.py', 'source/tensor/attribute.py', 'source/tensor/creation.py', 'source/tensor/einsum.py', 'source/tensor/__init__.py', 'source/tensor/random.py', 'source/tensor/logic.py', 'source/tensor/tensor.py', 'source/tensor/ops.py', 'source/tensor/layer_function_generator.py', 'source/tensor/linalg.py', 'source/tensor/stat.py', 'source/tensor/to_string.py', 'source/tensor/search.py', 'source/tensor/math.py', 'source/tensor/array.py']
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
