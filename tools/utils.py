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


def dump_func(name: str, inputs: list, outputs: list, defaults: list, hint=True):
    if hint:
        inputs = [
            f"{n}: {t}" for t, n in inputs
        ]
        for i, v in enumerate(defaults, 1):
            inputs[len(inputs) - i] += f" = {v}"
        inputs = ", ".join(inputs)
        if len(outputs) == 1:
            outputs = f"{outputs[0]}"
        else:
            outputs = f"list{outputs}"
        return f"def {name}({inputs}, name: str = None) -> {outputs}: \n"
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
                "args": [arg.arg for arg in node.args.args[:-1]],  # end args is 'name'
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

    with open(source_path, mode="w") as file:
        file.write("".join(lines))

    return replaced, not_replaced
