#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2022/11/27 16:52
# @Author : Rongrui Zhan
# @desc : 本代码未经授权禁止商用
from __future__ import annotations
from tools.utils import load_parsed_yaml, get_source_func, dump_func, replace_paddle


yaml_paths = ['tools/yaml/parsed_apis/api.parsed.yaml',
              'tools/yaml/parsed_apis/legacy_api.parsed.yaml',
              'tools/yaml/parsed_apis/backward_api.parsed.yaml',
              'tools/yaml/parsed_apis/legacy_backward_api.parsed.yaml']
yaml_funcs = {}
for yaml_path in yaml_paths:
    yaml_funcs.update(load_parsed_yaml(yaml_path))


source_paths = ['paddle/tensor/manipulation.py', 'paddle/tensor/attribute.py', 'paddle/tensor/creation.py',
                'paddle/tensor/einsum.py', 'paddle/tensor/random.py',
                'paddle/tensor/logic.py', 'paddle/tensor/ops.py',
                'paddle/tensor/layer_function_generator.py', 'paddle/tensor/linalg.py', 'paddle/tensor/stat.py',
                'paddle/tensor/to_string.py', 'paddle/tensor/search.py', 'paddle/tensor/math.py',
                'paddle/tensor/array.py']


all_not_replaced = {}
all_not_replaced_num = 0
all_replaced_num = 0
for source_path in source_paths:
    replaced, not_replaced = replace_paddle(source_path, yaml_funcs, inplace=True)
    all_not_replaced[source_path] = (f"{len(replaced)}/{len(replaced) + len(not_replaced)}")
    all_not_replaced_num += len(not_replaced)
    all_replaced_num += len(replaced)

print(all_not_replaced)
print(all_not_replaced_num)
print(all_replaced_num)
