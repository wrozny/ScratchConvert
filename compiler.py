import parser
import scratch
import scratch_constants
from scratch_constants import Opcodes
from tokenizer import tokenize


class Compiler:
    def __init__(self):
        self.tokens = []
        self.parser = None
        self.tree = []
        self.project = None
        self.last_stack = None

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
        if parent_stack == "update":
            update_stack = scratch.BlockStack()
            update_stack.add_block(scratch.Block(opcode=scratch_constants.Opcodes.EVENT_WHENFLAGCLICKED.value))

            substack_first_block_id = scratch.generate_uuid()

            substack_info = {}
            if len(func_tree) != 0:
                substack_info = {"SUBSTACK": [scratch_constants.Inputs.STATEMENT_RESULT.value, substack_first_block_id]}

            forever_block = scratch.Block(
                opcode=scratch_constants.Opcodes.CONTROL_FOREVER.value,
                inputs=substack_info
            )

            update_stack.add_block(forever_block)

            forever_substack = scratch.BlockStack(start_with_id=substack_first_block_id,
                                                  previous_block_id=forever_block.id)
            sprite_obj.block_stacks["update"] = update_stack
            sprite_obj.block_stacks[substack_first_block_id] = forever_substack
            return self._compile_func_tree(sprite_obj=sprite_obj, func_tree=func_tree,
                                           parent_stack=substack_first_block_id)

        for instruction in func_tree:
            match instruction[0]:
                case "assign":
                    variable_identifier_chunks = instruction[1].split(".")

                    variable_name: str
                    variable_id: str

                    if len(variable_identifier_chunks) == 1:
                        variable_name = instruction[1]
                        variable_id = instruction[1]
                    else:
                        variable_name = variable_identifier_chunks[1]
                        variable_id = instruction[1]

                    expression = scratch.Expression(expression_tokens=instruction[2])

                    setter_block = scratch.Block(
                        opcode=Opcodes.DATA_SETVARIABLETO.value,
                        inputs={"VALUE": expression.parse(target="set")},
                        fields={"VARIABLE": [variable_name, variable_id]}
                    )

                    for block in expression.blocks:
                        sprite_obj.data["blocks"][block.id] = block.data

                    sprite_obj.block_stacks[parent_stack].add_block(setter_block)

                case "if":
                    expression_tokens = instruction[1]
                    expression = scratch.Expression(expression_tokens=expression_tokens)

                    stack_starting_block_id = scratch.generate_uuid()

                    inputs_info = {
                        "CONDITION": expression.parse(target="compare"),
                        "SUBSTACK": [scratch_constants.Inputs.STATEMENT_RESULT.value, stack_starting_block_id]
                    }

                    if len(func_tree) == 0:
                        inputs_info["SUBSTACK"].pop("SUBSTACK")

                    if_statement = scratch.Block(
                        opcode=Opcodes.CONTROL_IF.value,
                        inputs=inputs_info
                    )

                    for block in expression.blocks:
                        sprite_obj.data["blocks"][block.id] = block.data

                    sprite_obj.block_stacks[parent_stack].add_block(if_statement)

                    new_block_stack = scratch.BlockStack(start_with_id=stack_starting_block_id,
                                                         previous_block_id=if_statement.id)
                    sprite_obj.block_stacks[stack_starting_block_id] = new_block_stack

                    self.last_stack = parent_stack
                    self._compile_func_tree(sprite_obj=sprite_obj, func_tree=instruction[2],
                                            parent_stack=stack_starting_block_id)
                case "call_method":
                    expression = scratch.Expression(expression_tokens=instruction[2][0])
                    method_name = instruction[1].split(".")[-1]

                    opcode = scratch_constants.method_to_opcode_map[method_name]
                    input_name = scratch_constants.opcode_to_input_name_map[opcode]
                    new_block = scratch.Block(
                        opcode=opcode,
                        inputs={input_name: expression.parse(target="set")}
                    )

                    for block in expression.blocks:
                        sprite_obj.data["blocks"][block.id] = block.data

                    sprite_obj.block_stacks[parent_stack].add_block(new_block)

    def _compile_function(self, sprite_obj, func_tree):
        func_chunks = func_tree[1].split(".")

        if len(func_chunks) == 1:
            return self._compile_func_tree(sprite_obj=sprite_obj, func_tree=func_tree[3],
                                           parent_stack=scratch.generate_uuid())
        return self._compile_func_tree(sprite_obj=sprite_obj, func_tree=func_tree[3], parent_stack=func_chunks[1])

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

            input_token = ["NUMBER" if isinstance(variable_initial_value, (int, float)) else "STRING",
                           variable_initial_value]

            expression = scratch.Expression(expression_tokens=[input_token])

            setter_block = scratch.Block(
                opcode=Opcodes.DATA_SETVARIABLETO.value,
                inputs={"VALUE": expression.parse()},
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

        for block_stack_id in sprite.block_stacks:
            for block in sprite.block_stacks[block_stack_id].get_blocks():
                sprite.set_block(block.id, block.data)

        self.project.add_sprite(sprite=sprite.data)
