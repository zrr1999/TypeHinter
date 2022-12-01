from __future__ import annotations

import ast
import re
import yaml


def load_parsed_yaml(path: str) -> dict[str, tuple[list, list]]:
    func_list = {}
    with open(path, 'r') as f:
        api_list = yaml.load(f, Loader=yaml.FullLoader)
    for api in api_list:
        api_name = api["name"]
        if api_name == "transpose":
            print(api)
        api_inputs = api["inputs"]
        api_outputs = api["outputs"]
        inputs = map(lambda inp: (inp["typename"], inp["name"]), api_inputs)
        outputs = map(lambda out: out["typename"], api_outputs)
        func_list[api_name] = (list(inputs), list(outputs))
    return func_list


def type_mapping(origin_type: str):
    if origin_type.endswith("[]"):
        return f"list[{origin_type[:-2]}]"
    else:
        return origin_type


def dump_func(name: str, inputs: list, outputs: list, defaults: list, end_arg: str|tuple[str, str], hint: bool = True):
    if hint:
        inputs = [
            f"{n}: {type_mapping(t)}" for t, n in inputs
        ]
        for i, v in enumerate(defaults, 1):
            inputs[len(inputs) - i] += f" = {v}"
        inputs = ", ".join(inputs)
        if len(outputs) == 1:
            outputs = f"{type_mapping(outputs[0])}"
        else:
            outputs = ", ".join(type_mapping(t) for t in outputs)
            outputs = f"tuple[{outputs}]"

        if not isinstance(end_arg, str):
            if end_arg[0] == "name":
                end_arg = "name: str = None"
            else:
                if end_arg[1] is not None:
                    end_arg = f"{end_arg[0]}: {type(end_arg[1]).__name__} = {end_arg[1]}"
                else:
                    end_arg = f"{end_arg[0]}={end_arg[1]}"
        return f"def {name}({inputs}, {end_arg}) -> {outputs}: \n"
    else:
        inputs = ", ".join([
            n for t, n in inputs
        ])
        return f"def {name}({inputs}, name=None):\n"


def replace_func(source: str, name: str, inputs: list, outputs: list, lineno: int):
    old_func = dump_func(name, inputs, outputs)
    new_func = dump_func(name, inputs, outputs, hint=True)
    # print(old_func, new_func)
    return source.replace(old_func, new_func)


def get_source_func(module: ast.Module):
    res = []
    for node in module.body:
        if isinstance(node, ast.FunctionDef):
            res.append({
                "name": node.name,
                "args": [arg.arg for arg in node.args.args],
                "defaults": [default.value if isinstance(default, ast.Constant) else NotImplementedError
                             for default in node.args.defaults],
                "lineno": node.lineno
            })
    return res


def replace_paddle(source_path: str, yaml_funcs: dict[str, tuple[list, list]], inplace=True):
    assert inplace  # TODO: not inplace mode

    not_replaced = []
    replaced = []
    with open(source_path, 'r') as file:
        lines = file.readlines()
        source = "".join(lines)
        module = ast.parse(source)
        source_funcs = get_source_func(module)

    for func in source_funcs:
        yaml_func = yaml_funcs.get(func["name"])

        if yaml_func is None or (len(func["args"]) != len(yaml_func[0]) + 1):
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
                end_arg = (func["args"][-1], func["defaults"][-1]) if func["defaults"] else func["args"][-1]
                lines[func["lineno"] - 1] = dump_func(func["name"], *yaml_func, func["defaults"][:-1],
                                                      end_arg=end_arg)
                replaced.append((func, yaml_func))

    with open(source_path, mode="w") as file:
        # import Tensor
        lines.insert(13,
                     "from __future__ import annotations\n"
                     "from typing import TYPE_CHECKING\n"
                     "if TYPE_CHECKING:\n"
                     "    from .tensor import Tensor\n")
        file.write("".join(lines))

    return replaced, not_replaced
