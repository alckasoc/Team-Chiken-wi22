import json
import os
import random

import sympy
from tqdm import tqdm

COMMON_PREAMBLE = None

# TODO: figure out how to usepackage without
# messing up the image size
r"""
\usepackage{amsmath}
\documentclass{article}

"""

MAX_TOKENS = 7
DATA_DIR = "data"

TOKENS = (
    "equiv",
    "oint",
    "int",
    "implies",
    "forall",
    "exists",
    "alpha",
    "beta",
    "gamma",
    "delta",
    "epsilon",
    "zeta",
    "eta",
    "theta",
    "iota",
    "kappa",
    "lambda",
    "mu",
    "tau",
    "pi",
    "leftarrow",
    "rightarrow",
    "infty",
    "neq",
    "approx",
    "times",
    "cup",
    "cap",
)


def write_image(tex: str, fn: str):
    tex = f"$${tex}$$"
    if os.path.exists(fn):
        raise FileExistsError(fn)

    sympy.preview(
        tex, viewer="file", filename=fn, euler=False, preamble=COMMON_PREAMBLE
    )


def random_latex_string(length: int) -> str:
    tokens = (f"\\{random.choice(TOKENS)}" for _ in range(length))
    return " ".join(tokens)


def generate_dataset(num_images: int):
    os.makedirs(DATA_DIR)
    map: dict[str, str] = {}

    for i in tqdm(range(num_images)):
        tex = random_latex_string(random.randint(1, MAX_TOKENS))
        fn = f"{DATA_DIR}/data_{i}.png"
        write_image(tex, fn)
        map[fn] = tex

    with open(f"{DATA_DIR}/index.json", "w") as f:
        json.dump(map, f)


if __name__ == "__main__":
    generate_dataset(50)
