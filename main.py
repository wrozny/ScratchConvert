import os

import zipper
import scratch
import tokenizer
from parser import Parser

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
SRC_DIR = os.path.join(SCRIPT_PATH, "src")
MAIN_FILE_PATH = os.path.join(SRC_DIR, "main.sl")


def main():
    if not os.path.isfile(MAIN_FILE_PATH):
        return print("No 'main.sl' file in src directory!")

    file_content: str
    with open(MAIN_FILE_PATH, "r") as file:
        file_content = file.read()

    tokens = tokenizer.tokenize(file_content)
    parser = Parser(tokens=tokens)
    tree = parser.parse()

    sprites = {}
    for sprite_name in parser.sprites:
        sprite_obj = scratch.Sprite(sprite_name)
        sprite = parser.sprites[sprite_name]
        for variable_name in sprite["variables"]:
            variable_initial_value = sprite["variables"][variable_name]
            sprite_obj.create_variable(name=variable_name, initial_value=variable_initial_value)
        sprites[sprite_name] = sprite_obj

    project = scratch.Project()
    for sprite_name in sprites:
        project.add_sprite(sprites[sprite_name])

    project.build_project()
    zipper.build_sb3()


if __name__ == '__main__':
    main()
