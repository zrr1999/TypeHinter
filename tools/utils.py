from __future__ import annotations
import re
import yaml


def load_api_yaml(path: str, use_pyparsing:bool=False) -> list[tuple[str, list, list]]:
    if use_pyparsing:
        raise NotImplementedError
    else:
        match_args = re.compile(r"\(?([_A-z0-9]+)\s+"
                                r"([_()A-z0-9]+)\s*"
                                r"(?==\s+([_A-z0-9]+))?\)?")
        match_outputs = re.compile(r"([_A-z0-9]+)\s*"
                                   r"(?!\([_A-z0-9]+\))?")

        func_list = []
        with open(path, 'r') as f:
            api_list = yaml.load(f, Loader=yaml.FullLoader)
        for api in api_list:
            api_name = api.get("backward_op", api.get("op"))
            api_args = api["args"]
            api_outs = api["output"]
            # api_name = api.get("backward_op", api.get("op"))
            # api_args = api.get("inputs", api.get("args"))
            # api_outs = api.get("outputs", api.get("output"))
            args = []
            for e in api_args.split(","):
                match_res = match_args.findall(e)
                if match_res:
                    args.append(match_res[0][:2])
            outs = [match_outputs.findall(e)[0] for e in api_outs.split(",")]
            func_list.append((api_name, args, outs))
    return func_list


def dump_func(name: str, inputs: list, outputs: list, hint=False):
    if hint:
        inputs = ", ".join([
            f"{n}: {t}" for t, n in inputs
        ])
        if len(outputs) == 1:
            outputs = f"{outputs[0]}"
        else:
            outputs = f"typing.List{outputs}"
        return f"def {name}({inputs}, name: str = None) -> {outputs}: "
    else:
        inputs = ", ".join([
            n for t, n in inputs
        ])
        return f"def {name}({inputs}, name=None):"


def replace_func(source: str, name: str, inputs: list, outputs: list):
    old_func = dump_func(name, inputs, outputs)
    new_func = dump_func(name, inputs, outputs, hint=True)
    return source.replace(old_func, new_func)
