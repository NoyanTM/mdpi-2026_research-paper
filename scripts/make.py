import os
import subprocess
import argparse
import pathlib
import dataclasses


@dataclasses.dataclass
class Config:
    BASE_DIRECTORY: pathlib.Path = pathlib.Path(__file__).parent.parent
    INPUT_DIRECTORY: pathlib.Path = BASE_DIRECTORY / "paper"
    OUTPUT_DIRECTORY: pathlib.Path = BASE_DIRECTORY / "build"


def create_cli_parser(commands: list[dict]) -> argparse.ArgumentParser:
    cli_parser = argparse.ArgumentParser()
    subparsers = cli_parser.add_subparsers(dest="command")
    for command in commands:
        sub = subparsers.add_parser(name=command["command"], description=command["description"])
        if not command["arguments"]:
            continue
        for arg in command["arguments"]:
            sub.add_argument(*arg["args"], **arg["kwargs"])
    return cli_parser


def handle_commands(args, config: Config, commands: list[dict]):
    if not args.command:
        error = f"Must used be one of available commands: {[command["command"] for command in commands]}"
        raise Exception(error)
    for command in commands:
        if command["command"] == args.command:
            try:
                command["func"](config, **vars(args))
            except Exception:
                raise
            break


def _compile_paper(config, *args, **kwargs):
    input_path = kwargs["input"]
    output_path = kwargs["output"]

    if not input_path:
        config.INPUT_DIRECTORY.mkdir(exist_ok=True)
        input_path = config.INPUT_DIRECTORY
    if not output_path:
        config.OUTPUT_DIRECTORY.mkdir(exist_ok=True)
        output_path = config.OUTPUT_DIRECTORY
    
    errors = []
    pdflatex_cmd = [
        "pdflatex", f"--output-directory={str(output_path)}", "-no-shell-escape", "-halt-on-error",
        "-shell-restricted", "-interaction=nonstopmode", f"{str(input_path / "template.tex")}"
    ]
    pdflatex_env = os.environ.copy()
    pdflatex_env.update({"TEXINPUTS": f".:{str(input_path)}//:"})

    # need to run pdflatex multiple times due to cross-references
    for i in range(3):
        result = subprocess.run(args=pdflatex_cmd, env=pdflatex_env, capture_output=True)
        if result.returncode != 0:
            error = f"Error occured during building document from source or calling tools: {result.stdout.decode()}" # because pdflatex does not return errors to stderr
            errors.append(error)
    if errors:
        raise Exception("\n".join(errors))


_commands = [
    {
        "command": "all",
        "description": "run diagrams, paper, and docs commands",
        "arguments": [],
        "func": ...
    },
    {
        "command": "paper",
        "description": "compile paper via pdflatex and optional biber with jinja templating",
        "arguments": [
            {
                "args": ("--input", "-i"),
                "kwargs": {"help": "input path, default: REPO_PATH/paper", "type": str}
            },
            {
                "args": ("--output", "-o"),
                "kwargs": {"help": "output path, default: REPO_PATH/paper", "type": str}
            },
        ],
        "func": _compile_paper
    },
    {
        "command": "diagrams",
        "description": "build additional diagrams from graphviz and plantuml formats",
        "arguments": [],
        "func": ...
    },
    {
        "command": "docs",
        "description": "build sphinx documentation for the practical part",
        "arguments": [],
        "func": ...
    },
    {
        "command": "clean",
        "description": "clean cache and temporary files from build operations",
        "arguments": [],
        "func": ...
    }
]


def main():
    config = Config()
    cli_parser = create_cli_parser(_commands)
    handle_commands(cli_parser.parse_args(), config, _commands)


if __name__ == "__main__":
    main()
