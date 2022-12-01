#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2022/11/27 16:52
# @Author : Rongrui Zhan
# @desc : 本代码未经授权禁止商用
from __future__ import annotations
import os
import subprocess
import typing
import ast
import numpy as np
from tools.utils import load_parsed_yaml, get_source_func, dump_func

if not os.path.exists("generated/tensor"):
    if not os.path.exists("generated"):
        os.mkdir("generated")
    os.mkdir("generated/tensor")

yaml_dir = "tools/parsed_ops/"
yaml_paths = os.listdir(yaml_dir)
yaml_funcs = {}
for yaml_path in yaml_paths:
    yaml_funcs.update(load_parsed_yaml(yaml_dir+yaml_path))

source_paths = ['source/tensor/manipulation.py', 'source/tensor/attribute.py', 'source/tensor/creation.py',
                'source/tensor/einsum.py', 'source/tensor/random.py',
                'source/tensor/logic.py', 'source/tensor/ops.py',
                'source/tensor/layer_function_generator.py', 'source/tensor/linalg.py', 'source/tensor/stat.py',
                'source/tensor/to_string.py', 'source/tensor/search.py', 'source/tensor/math.py',
                'source/tensor/array.py']


all_not_replaced = {}
all_not_replaced_num = 0
all_replaced_num = 0
for source_path in source_paths:
    not_replaced = []
    replaced = []
    with open(source_path, 'r') as file:
        lines = file.readlines()
        source = "".join(lines)
        module = ast.parse(source)
        source_funcs = get_source_func(module)

    for func in source_funcs:
        yaml_func = yaml_funcs.get(func["name"])

        if func["name"] == "divide":
            print(1)

        if yaml_func is None or (len(func["args"]) != len(yaml_func[0])):
            # print(func["name"], len(func["args"]))
            not_replaced.append((func, yaml_func))
        else:
            matched = True
            for a, ya in zip(func["args"], yaml_func[0]):
                if a != ya[1]:
                    not_replaced.append((func, yaml_func))
                    matched = False
                    print(func["name"], a, ya)
                    break
            if matched:
                lines[func["lineno"] - 1] = dump_func(func["name"], *yaml_func, func["defaults"])

                # print(lines[func["lineno"]])
                replaced.append((func, yaml_func))

    # if len(not_replaced):
    all_not_replaced[source_path] = (f"{len(replaced)}/{len(replaced) + len(not_replaced)}")
    all_not_replaced_num += len(not_replaced)
    all_replaced_num += len(replaced)
    with open(source_path.replace("source", "generated"), mode="w") as stub_file:
        stub_file.write("".join(lines))

print(all_not_replaced)
print(all_not_replaced_num)
print(all_replaced_num)
