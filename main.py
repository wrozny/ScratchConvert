import os

import zipper
from compiler import Compiler

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.join(SCRIPT_PATH, "src")
MAIN_FILE_PATH = os.path.join(SRC_DIR, "main.sl")
BUILD_DIR_PATH = os.path.join(SCRIPT_PATH, "build")
PROJECT_DIR_PATH = os.path.join(BUILD_DIR_PATH, "project")


def main():
    if not os.path.isfile(MAIN_FILE_PATH):
        return print("No 'main.sl' file in src directory!")

    file_content: str
    with open(MAIN_FILE_PATH, "r") as file:
        file_content = file.read()

    compiler = Compiler()
    compiler.compile(file_content=file_content)
    compiler.project.build_project(output_directory=PROJECT_DIR_PATH)

    zipper.build_sb3()


if __name__ == '__main__':
    main()
