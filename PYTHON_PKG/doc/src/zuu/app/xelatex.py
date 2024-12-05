import os
import typing
from zuu.common.tempFile import temp

def run_xelatex(
    file : str,
    args : typing.List[str] = [],
    texInputs : str = None
):
    if texInputs is not None:
        texInputs = '-include-directory="{texInputs}"'
    else:
        texInputs = ""

    os.system(f"xelatex -interaction=nonstopmode {file} {texInputs} {' '.join(args)}")

def run_xelatex_in_temp(
    folder : str,
    captures : typing.List[str],
    args : typing.List[str] = [],
    texInputs : str = None
):
    
    for file in os.listdir(folder):
        if file.endswith(".tex"):
            texFile = file
            break

    temp(
        paths = [
            f"{folder}/*",
        ],
        capture = captures,
    )(
        lambda: run_xelatex(texFile, args, texInputs)
    )()