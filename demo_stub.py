#!/usr/bin/env python
# _*_ coding: utf-8 _*_
# @Time : 2022/11/27 16:52
# @Author : Rongrui Zhan
# @desc : 本代码未经授权禁止商用
import re

import yaml


def gen_func_stub(name, inputs: list, outputs: list):
    args = ", ".join([
        f"{n}: {t}" for t, n in inputs
    ])
    if len(outputs) == 1:
        outputs = f"{outputs[0]}"
    else:
        outputs = f"typing.List{outputs}"
    return f"def {name}({args}) -> {outputs}: ..."


match_args = re.compile(r"\(([_A-z0-9]+)\s+"
                        r"([_A-z0-9]+)\s*"
                        r"(?==\s+([_A-z0-9]+))?\)")
match_outputs = re.compile(r"([_A-z0-9]+)\s*"
                           r"(\([_A-z0-9]+\))?")
api_yaml_path = ["ops.yaml"]
for each_api_yaml in api_yaml_path:
    stub_list = []
    with open(each_api_yaml, 'r') as f:
        api_list = yaml.load(f, Loader=yaml.FullLoader) or []
        for api in api_list:
            op_name = api["op"]
            op_args = api["args"]
            op_outs = api["output"]
            args = []
            for e in op_args.split(","):
                result = match_args.findall(e)
                if result:
                    args.append([result[0][0], result[0][1]])
            outs = []
            for e in op_outs.split(","):
                result = match_outputs.findall(e)
                if result:
                    outs.append(result[0][0])
            stub_list.append(gen_func_stub(op_name, args, outs))

    with open(each_api_yaml.replace("yaml", "pyi"), mode="w") as stub_file:
        stub_file.write("import typing\n")
        stub_file.write("from paddle import Tensor\n")
        stub_file.write("\n".join(stub_list))


# import paddle
#
# print(paddle.add().)
