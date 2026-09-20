#!/usr/bin/emv python3
# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
#
# appn_summarizer.py
#
# Summarise RO-Crate contents
#
# -----------------------------------------------------------------------------
# Created By  : Donald Hobern, donald.hobern@adelaide.edu.au
# Created Date: 2026-08-20
# version ='2026.0.1'
# -----------------------------------------------------------------------------

import argparse
import logging
import sys

from pathlib import Path
from typing import Any, Optional

from appn_configuration import APPN_SCHEMA
from appn_dictionary import Dictionary

### setup_parser ##############################################################


def setup_parser() -> argparse.ArgumentParser:
    """
    Set up parser to handle command-line sys.argv parameters or
    interactive parameters in the same format.

    The parser handles the following arguments:
      -l, --log-level         : "info" / "warning" / "error" / "debug".
      -e, --echo-to-stderr    : Display logging outputs to stderr.
      -a, --asset             : Namespace for an asset to be loaded - may be repeated.
      -p, --prefix            : (Optional) Prefix for asset to be loaded - the n-th prefix is used for the n-th asset.
      -f, --filepath-to-asset : (Optional) Filepath for reading asset instead of via URL - the n-th filepath is used for the n-th asset.
    """
    parser = argparse.ArgumentParser(
        description=f"{__name__}: Summarise RO-Crate contents"
    )

    parser.add_argument(
        "-l",
        "--log-level",
        choices=("error", "warning", "info", "debug"),
        default="info",
        help="Set logging level",
    )
    parser.add_argument(
        "-e",
        "--echo-to-stderr",
        action=argparse.BooleanOptionalAction,
        default=False,
        help="Echo log messages to console",
    )
    parser.add_argument(
        "-a",
        "--asset",
        action="append",
        help="Namespace for linked-data asset to load into graph.",
    )
    parser.add_argument(
        "-p", "--prefix", action="append", help="Optional prefix for loaded asset."
    )
    parser.add_argument(
        "-f",
        "--filepath_to_asset",
        action="append",
        help="Path to asset file if different from asset namespace.",
    )

    return parser


### start_log #################################################################
#
# Start logging to default or named file and optionally to stderr.
#
#     level             : info / error / debug (string or logging enumeration).
#     name              : (optional) name for log file.
#     echo              : boolean - duplicate logging to stderr
#
def start_log(
    level: str | int = logging.INFO, name: Optional[str] = None, echo: bool = True
) -> None:
    if isinstance(level, str):
        level = level.lower()
        if level == "error":
            log_level = logging.ERROR
        elif level == "debug":
            log_level = logging.DEBUG
        else:
            log_level = logging.INFO
    else:
        log_level = level

    if name is None:
        name = Path(sys.argv[0]).stem
    logfile_name = f"{name}.log"
    logging.basicConfig(
        filename=logfile_name,
        filemode="w",
        level=log_level,
        format="%(asctime)s %(levelname)s %(filename)s : %(lineno)s - %(funcName)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    if echo:
        logging.getLogger().addHandler(logging.StreamHandler())

    logging.info(f"Logging started to {logfile_name} at level {level} and echo {echo}")


if __name__ == "__main__":

    parser = setup_parser()
    args = vars(parser.parse_args(sys.argv[1:]))
    start_log(args["log_level"], None, args["echo_to_stderr"])

    d = Dictionary()
    d.load(APPN_SCHEMA)
    if args["asset"] is not None:
        for i in range(len(args["asset"])):
            asset = args["asset"][i]
            if args["prefix"] is not None and i in range(len(args["prefix"])):
                prefix = args["prefix"][i]
            else:
                prefix = None
            if args["filepath_to_asset"] is not None and i in range(
                len(args["filepath_to_asset"])
            ):
                path = args["filepath_to_asset"][i]
            else:
                path = None
            d.load(asset, asset_path=path, asset_prefix=prefix)
    d.import_references()

    for study in d.list_instances("appn:Study"):
        print(d.describe(study))

    logging.info("Finished")
