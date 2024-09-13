import json
import os
from ScratchConstants import *
from string import ascii_letters
from random import choice

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BUILD_DIR_PATH = os.path.join(SCRIPT_PATH, "build")
PROJECT_DIR_PATH = os.path.join(BUILD_DIR_PATH, "project")

LETTERS = [*ascii_letters]


def generate_uuid():
    return "".join([choice(LETTERS) for _ in range(32)])


class Expression:
    def __init__(self):
        self.id = generate_uuid()


class Block:
    def __init__(self, opcode, args=None):
        self.opcode = opcode
        self.args = args
        self.id = generate_uuid()

    def compile(self, parent_block=None, next_block=None):
        block = BLOCK_BASE.copy()
        block["next"] = next_block
        block["parent"] = parent_block
        block["opcode"] = self.opcode
        block["inputs"] = self.args or {}
        return self.id, block


class BlockStack:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def compile_stack(self, previous_stack_end_block_id=None, next_stack_start_id=None):
        results = {}
        previous_block = previous_stack_end_block_id
        stack_length = len(self.blocks)

        for block_index, block in enumerate(self.blocks):
            next_block_id = next_stack_start_id
            if not block.id == self.blocks[stack_length - 1].id:
                next_block_id = self.blocks[block_index + 1].id

            previous_block, block_data = block.compile(parent_block=previous_block, next_block=next_block_id)
            if block_index == 0 and previous_stack_end_block_id is None:
                block_data["topLevel"] = True
                block_data["x"] = 0
                block_data["y"] = 0

            results[previous_block] = block_data

        return results


class Sprite:
    def __init__(self, name):
        self.block_stack = None
        self.name = name

    def set_block_stack(self, block_stack):
        self.block_stack = block_stack

    def compile(self):
        sprite = SPRITE_BASE.copy()
        sprite["name"] = self.name
        sprite_blocks = self.block_stack.compile_stack()

        for block_id in sprite_blocks:
            sprite["blocks"][block_id] = sprite_blocks[block_id]

        # compile blocks and put them inside the sprite
        return sprite


class Project:
    def __init__(self):
        self.sprites = []

    def add_sprite(self, sprite):
        self.sprites.append(sprite)

    def build_project(self, output_directory=PROJECT_DIR_PATH):
        project = PROJECT_BASE.copy()
        project["targets"].append(DEFAULT_STAGE.copy())  # add empty stage to the project

        for sprite in self.sprites:
            project["targets"].append(sprite.compile())

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        project_json_path = os.path.join(output_directory, "project.json")
        with open(project_json_path, "w") as output:
            json_output = json.dumps(project)
            output.write(json_output)
