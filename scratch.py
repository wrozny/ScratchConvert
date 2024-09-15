import json
import os
from scratch_constants import *
from string import ascii_letters
from random import choice

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
BUILD_DIR_PATH = os.path.join(SCRIPT_PATH, "build")
PROJECT_DIR_PATH = os.path.join(BUILD_DIR_PATH, "project")

LETTERS = [*ascii_letters]


def generate_uuid():
    return "".join([choice(LETTERS) for _ in range(16)])


class Expression:
    def __init__(self):
        self.id = generate_uuid()


class Block:
    def __init__(self, opcode, inputs=None, fields=None):
        self.opcode = opcode
        self.inputs = inputs
        self.fields = fields
        self.id = generate_uuid()

    def compile(self, parent_block=None, next_block=None):
        block = BLOCK_BASE.copy()
        block["next"] = next_block
        block["parent"] = parent_block
        block["opcode"] = self.opcode
        block["inputs"] = self.inputs or {}
        block["fields"] = self.fields or {}
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
        self.name = name
        self.variables = {}

    def get_variable_id(self, name):
        return name + f"-{self.name}"

    def create_variable(self, name, initial_value):
        self.variables[self.get_variable_id(name)] = [name, initial_value]

    def compile(self):
        sprite = SPRITE_BASE.copy()
        sprite["name"] = self.name

        variables = {}
        for variable_id in self.variables:
            variable_data = self.variables[variable_id]
            variable_name = variable_data[0]
            initial_value = variable_data[1] or ""
            variables[variable_id] = [variable_name, initial_value]

        sprite["variables"] = variables

        # variable initial setters

        setters_block_stack = BlockStack()
        setters_block_stack.add_block(Block(opcode="event_whenflagclicked"))

        for variable_name in self.variables:
            variable_data = self.variables[variable_name]
            block = Block(
                opcode="data_setvariableto",
                inputs={"VALUE": [1, [10, variable_data[1] or ""]]},
                fields={"VARIABLE": [variable_data[0], self.get_variable_id(variable_data[0])]}
            )
            setters_block_stack.add_block(block)

        setters_output = setters_block_stack.compile_stack()
        for block_id in setters_output:
            sprite["blocks"][block_id] = setters_output[block_id]

        sprite["blocks"] = setters_output
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
