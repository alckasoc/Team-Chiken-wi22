import concurrent.futures
import json
import multiprocessing
import os
import random

import click
import sympy
from tqdm import tqdm

COMMON_PREAMBLE = None

# TODO: figure out how to usepackage without
# messing up the image size
r"""
\usepackage{amsmath}
\documentclass{article}

"""

# maximum token length of a generated latex string
MAX_TOKENS = 7
# name of the directory to put the images
DATA_DIR = "data"

# These are the latex commands that we are choosing from (feel free to add more!)
# for example "\int" will render an integral symbol and "\pi" will render an image of π
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
    """Create a png file that contains the rendered latex code.

    :param tex: Latex code to render
    :type tex: str
    :param fn: Name of the file
    :type fn: str
    """
    # You need to surround math symbols with $$'s
    tex = f"$${tex}$$"
    if os.path.exists(fn):
        raise FileExistsError(fn)

    # This just opens a `latex` process that generates the image for us
    sympy.preview(
        tex, viewer="file", filename=fn, euler=False, preamble=COMMON_PREAMBLE
    )


def random_latex_string(length: int) -> str:
    """Choose random latex tokens, and combine them into a latex code
    string that can be rendered.

    :param length: Number of tokens to include in string
    :type length: int
    :rtype: str
    """
    tokens = (f"\\{random.choice(TOKENS)}" for _ in range(length))
    return " ".join(tokens)


def generate_dataset(num_images: int):
    """Concurrently generate random latex strings and render them.
    All we're doing here is running multiple processes at once so that
    we don't have to wait for the previous image to render before starting
    the next one.

    :param num_images: Number of images to generate
    :type num_images: int
    """

    os.makedirs(DATA_DIR)
    # a map from image filename to the latex code that rendered it
    # this will eventually be stored in a json file
    index: dict[str, str] = {}

    # This is the function that every "worker" is sent out to do
    def _generate_aux(i: int):
        # create an image with a random latex string with variable width
        # update the index
        tex = random_latex_string(random.randint(1, MAX_TOKENS))
        fn = os.path.join(DATA_DIR, f"data_{i}.png")
        write_image(tex, fn)
        index[fn] = tex

    with concurrent.futures.ThreadPoolExecutor(
        # This is a good heuristic for cpu intensive tasks like image rendering
        max_workers=multiprocessing.cpu_count()
    ) as executor:
        # executor.submit starts running `_generate_aux(i)` for i from 0 to num_images
        futures = [executor.submit(_generate_aux, i) for i in range(num_images)]
        # as the tasks are completed update the progress bar
        for _ in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            pass

    # write the index to a json file
    with open(os.path.join(DATA_DIR, "index.json"), "w") as f:
        json.dump(index, f)


@click.command()
@click.argument("num_images")
def main(num_images):
    if os.path.exists("data"):
        print("generate_dataset.py: Delete or rename ./data")
        return
    generate_dataset(int(num_images))


if __name__ == "__main__":
    main()
