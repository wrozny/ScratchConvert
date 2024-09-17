import json
import os
from uuid import uuid4

import scratch_constants
from scratch_constants import *


def generate_uuid():
    return str(uuid4())


class Expression:
    def __init__(self, expression_tokens):
        self.expression_tokens = expression_tokens
        self.current_token_index = 0
        self.new_subject = None
        self.old_subject = None
        self.operation = None
        self.blocks = []

    def parse_token(self, token):
        match token[0]:
            case "STRING":
                return [scratch_constants.Inputs.DIRECT_INPUT.value,
                        [scratch_constants.Inputs.PLAIN_TEXT.value, token[1].strip(r'"')]]
            case "NUMBER":
                return [scratch_constants.Inputs.DIRECT_INPUT.value,
                        [scratch_constants.Inputs.PLAIN_TEXT.value, token[1]]]
            case "ARGUMENT":
                return self.parse_token(token=("STRING", "Argument will be parsed here instead! working on it"))
            case "VARIABLE":
                variable_name_split = token[1].split(".")
                variable_id = token[1]
                variable_name: str
                if len(variable_name_split) == 1:
                    variable_name = token[1]
                else:
                    variable_name = variable_name_split[1]

                input_value = [scratch_constants.Inputs.BLOCK_REFERENCE.value, [
                    scratch_constants.Inputs.VARIABLE_INPUT.value,
                    variable_name,
                    variable_id
                ]]

                return input_value
            case "BLOCK":
                return [scratch_constants.Inputs.BLOCK_REFERENCE.value, token[1]]

    def advance(self):
        self.current_token_index += 1

    def get_current_token(self):
        if (len(self.expression_tokens) - 1) < self.current_token_index:
            return None
        return self.expression_tokens[self.current_token_index]

    def expect_token(self, expected_tokens):
        current_token = self.get_current_token()

        if current_token is None and None in expected_tokens:
            return None

        if current_token[0] in expected_tokens:
            self.advance()
            return current_token
        else:
            raise Exception(f"Expected {expected_tokens}, got {current_token}")

    def parse(self, target="set"):
        if target == "compare":
            self.expression_tokens.append(("COMPARE", "=="))
            self.expression_tokens.append(("STRING", "true"))

        if len(self.expression_tokens) == 1:
            return self.parse_token(token=self.expression_tokens[0])

        while self.get_current_token() is not None:
            # Parse the first subject (e.g., a variable, number, or string)
            if not self.new_subject:
                self.new_subject = self.expect_token(["NUMBER", "STRING", "VARIABLE"])

            # Parse the operation (e.g., "+", "-", "==" etc.)
            self.operation = self.expect_token(["OP", "COMPARE", None])

            if self.operation:

                self.old_subject = self.blocks[-1] if len(self.blocks) > 0 else self.new_subject

                if isinstance(self.old_subject, Block):
                    self.old_subject = ("BLOCK", self.old_subject.id)

                self.new_subject = self.expect_token(["NUMBER", "STRING", "VARIABLE"])

                opcode = symbol_to_opcode_map[self.operation[1]]
                input_value_name = opcode_to_input_name_map[opcode]

                operation_block = Block(
                    opcode=opcode,
                    inputs={
                        f"{input_value_name}1": self.parse_token(self.old_subject),
                        f"{input_value_name}2": self.parse_token(self.new_subject)
                    }
                )

                self.blocks.append(operation_block)

                # Here we could build the expression block and return it or keep iterating for more complex expressions
        previous_block = None
        for block in self.blocks:
            if previous_block is not None:
                block.set_parent(previous_block)
                previous_block = block

        last_block_id = self.blocks[-1].id
        return [scratch_constants.Inputs.BLOCK_REFERENCE.value, last_block_id]


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
    def __init__(self, start_with_id=None, previous_block_id=None):
        self._blocks = []
        self._start_with_id = start_with_id
        self._previous_block_id = previous_block_id
        self._current_index = -1

    def add_block(self, block_obj):
        self._current_index += 1
        self._blocks.append(block_obj)
        if len(self._blocks) > 1:
            previous_block = self._blocks[self._current_index - 1]
            previous_block.set_next(block_obj.id)
            block_obj.set_parent(previous_block.id)

    def get_blocks(self, last_block=None):
        if len(self._blocks) == 0:
            return []

        if last_block is None:
            if self._start_with_id is not None:
                self._blocks[0].id = self._start_with_id
            elif self._previous_block_id is not None:
                self._blocks[0].set_parent(self._previous_block_id)
            else:
                self._blocks[0].set_level(True)
        else:
            self._blocks[0].set_parent(last_block.id)

            if self._start_with_id is not None:
                self._blocks[0].id = self._start_with_id
            if self._previous_block_id is not None:
                self._blocks[0].set_parent(self._previous_block_id)

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
