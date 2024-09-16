import json
import os
from uuid import uuid4

from scratch_constants import *


# SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))
# BUILD_DIR_PATH = os.path.join(SCRIPT_PATH, "build")
# PROJECT_DIR_PATH = os.path.join(BUILD_DIR_PATH, "project")


def generate_uuid():
    return str(uuid4())


class Expression:
    def __init__(self, expression_tokens):
        self.expression_tokens = expression_tokens

    def parse_single(self):
        match self.expression_tokens[0][0]:
            case "STRING":
                return self.expression_tokens[0][1].strip(r'"')
            case "NUMBER":
                return self.expression_tokens[0][1]
            case "ARGUMENT":
                return ""
            case "VARIABLE":
                return "Variable"

    def parse(self):
        if len(self.expression_tokens) == 1:
            return self.parse_single()

        return "complex expression"


class Block:
    def __init__(self, opcode, inputs=None, fields=None, is_top_level=False):
        self.data = BLOCK_BASE.copy()
        self.data["opcode"] = opcode
        self.data["inputs"] = inputs or {}
        self.data["fields"] = fields or {}
        self.set_level(is_top_level)
        self.id = generate_uuid()

    def set_next(self, next_block):
        self.data["next"] = next_block

    def set_parent(self, parent_block):
        self.data["parent"] = parent_block

    def set_level(self, is_top_level):
        if is_top_level:
            self.set_parent(parent_block=None)
            self.data["x"] = 0
            self.data["y"] = 0
            self.data["topLevel"] = is_top_level
        else:
            self.data.pop("x", None)
            self.data.pop("y", None)
            self.data["topLevel"] = is_top_level


class BlockStack:
    def __init__(self):
        self._blocks = []
        self._current_index = -1

    def add_block(self, block_obj):
        self._current_index += 1
        self._blocks.append(block_obj)
        if len(self._blocks) > 1:
            previous_block = self._blocks[self._current_index - 1]
            previous_block.set_next(block_obj.id)
            block_obj.set_parent(previous_block.id)

    def get_blocks(self, last_block=None):
        if last_block is None:
            self._blocks[0].set_level(True)
        else:
            self._blocks[0].set_parent(last_block.id)
        return self._blocks


class Sprite:
    def __init__(self, name):
        self.name = name
        self.data = SPRITE_BASE.copy()
        self.data["name"] = name
        self.block_stacks = {}

    def get_variable_id(self, name):
        return f"{self.name}.{name}"

    def create_variable(self, name, initial_value):
        variable_id = self.get_variable_id(name)
        self.data["variables"][variable_id] = [name, initial_value or ""]

    def set_block(self, block_id, block_data):
        self.data["blocks"][block_id] = block_data


class Project:
    def __init__(self):
        self.data = PROJECT_BASE.copy()
        self.stage = DEFAULT_STAGE.copy()
        self.data["targets"].append(self.stage)

    def add_sprite(self, sprite):
        self.data["targets"].append(sprite)

    def create_variable(self, variable_name, initial_value=None):
        self.stage["variables"][variable_name] = [variable_name, initial_value or ""]

    def build_project(self, output_directory):
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        project_json_path = os.path.join(output_directory, "project.json")
        with open(project_json_path, "w") as output:
            json_output = json.dumps(self.data)
            output.write(json_output)
