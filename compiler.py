import parser
import scratch
from scratch_constants import Opcodes
from tokenizer import tokenize


class Compiler:
    def __init__(self):
        self.tokens = []
        self.parser = None
        self.tree = []
        self.project = None

    def compile(self, file_content):
        self.tokens = tokenize(file_content)
        self.parser = parser.Parser(tokens=self.tokens)
        self.tree = self.parser.parse()
        self.project = scratch.Project()

        for sprite_name in self.parser.sprites:
            self._create_sprite(sprite_name=sprite_name)

        for variable_name in self.parser.global_variables:
            initial_value = self.parser.global_variables[variable_name]
            self.project.create_variable(variable_name=variable_name, initial_value=initial_value)

    def _compile_func_tree(self, sprite_obj, func_tree, parent_stack):
        for instruction in func_tree[3]:
            match instruction[0]:
                case "assign":
                    variable_identifier_chunks = instruction[1].split(".")
                    expression = scratch.Expression(expression_tokens=instruction[2])
                    input_value = expression.parse()

                    variable_name: str
                    variable_id: str

                    if len(variable_identifier_chunks) == 1:
                        variable_name = instruction[1]
                        variable_id = instruction[1]
                    else:
                        variable_name = variable_identifier_chunks[1]
                        variable_id = instruction[1]

                    setter_block = scratch.Block(
                        opcode=Opcodes.DATA_SETVARIABLETO.value,
                        inputs={"VALUE": [1, [10, input_value]]},
                        fields={"VARIABLE": [variable_name, variable_id]}
                    )

                    sprite_obj.block_stacks[parent_stack].add_block(setter_block)

    def _compile_start_func_tree(self, sprite_obj, func_tree):
        self._compile_func_tree(sprite_obj=sprite_obj, func_tree=func_tree, parent_stack="start")

        for block in sprite_obj.block_stacks["start"].get_blocks():
            sprite_obj.set_block(block.id, block.data)

    def _compile_function(self, sprite_obj, func_tree):
        func_chunks = func_tree[1].split(".")

        # global function
        if len(func_chunks) == 1:
            return None  # self._compile_func_tree()

        match func_chunks[1]:
            case "start":
                return self._compile_start_func_tree(sprite_obj=sprite_obj, func_tree=func_tree)
            case "update":
                return None  # self._compile_func_tree()

    def _create_sprite(self, sprite_name):
        sprite = scratch.Sprite(name=sprite_name)
        sprite_data = self.parser.sprites[sprite_name]
        variables = sprite_data["variables"]
        for variable_name in variables:
            variable_initial_value = variables[variable_name]
            sprite.create_variable(name=variable_name, initial_value=variable_initial_value)

        start_block_stack = scratch.BlockStack()
        sprite.block_stacks["start"] = start_block_stack
        start_block_stack.add_block(scratch.Block(opcode=Opcodes.EVENT_WHENFLAGCLICKED.value))

        for variable_id in sprite.data["variables"]:
            variable_data = sprite.data["variables"][variable_id]
            variable_name = variable_data[0]
            variable_initial_value = variable_data[1]

            if variable_initial_value == "":
                continue

            setter_block = scratch.Block(
                opcode=Opcodes.DATA_SETVARIABLETO.value,
                inputs={"VALUE": [1, [10, variable_initial_value or ""]]},
                fields={"VARIABLE": [variable_name, variable_id]}
            )

            start_block_stack.add_block(setter_block)

        for func_tree in self.tree:
            func_identifier = func_tree[1]
            func_identifier_chunks = func_identifier.split(".")
            is_sprite_function = (len(func_identifier_chunks) == 2 and func_identifier_chunks[0] == sprite_name)
            is_global_function = len(func_identifier_chunks) == 1

            if is_global_function or is_sprite_function:
                self._compile_function(sprite_obj=sprite, func_tree=func_tree)

        self.project.add_sprite(sprite=sprite.data)
