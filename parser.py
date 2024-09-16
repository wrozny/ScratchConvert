builtin_libraries = {
    "debug": ["log"]
}
sprite_methods = ["move_steps", "rotate_right", "rotate_left", "move_to"]


def remove_quotation_mark(value):
    if type(value) == str:
        return value.strip(r'"')
    return value


def _check_library(library_name, rest):
    if len(rest) == 1 and rest[0] in builtin_libraries[library_name]:
        return "function"
    if len(rest) == 1 and rest[0] in sprite_methods:
        return "method"

    return None


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.current_scope = "global"
        self.current_function_name = ""
        self.sprites = {}
        self.global_variables = {}
        self.global_functions = {}
        self.global_lists = []

    def parse(self):
        instructions = []
        while self.current_token_index < len(self.tokens):
            token = self.current_token()
            token_type = token[0]
            token_value = token[1]
            if token_type == 'KEYWORD':
                if token_value == 'create':
                    self.parse_create()
                elif token_value == 'define':
                    instructions.append(self.parse_define())
                elif token_value == 'var':
                    self.parse_variable()
                elif token_value == "if":
                    self.parse_if_statement()
                elif token_value == "repeat":
                    instructions.append(self.parse_repeat(repeat_type="repeat"))
                elif token_value == "repeat_until":
                    instructions.append(self.parse_repeat(repeat_type="repeat_until"))
            elif token_type == 'ID':
                # Can't call functions outside sprite's scope
                self.advance()
            else:
                self.advance()
        return instructions

    def get_identifier_type(self, identifier):
        chunks = identifier.split(".")

        if len(chunks) == 2:
            source_of_problems = self.get_temp_variable_identifier(chunks[1])  # is actually temp variable name and was source of problems, still is sometimes
            identifier_type = self._resolve_identifier(source_of_problems.split("."))
            if identifier_type is not None:
                return identifier_type, source_of_problems

        return self._resolve_identifier(chunks), identifier

    def _resolve_identifier(self, chunks):
        if not chunks:
            return None  # Base case: if there are no more chunks left

        if len(chunks) == 1:
            global_identifier = self._check_global_identifier_or_sprite(chunks[0])
            if global_identifier is not None:
                return global_identifier
            is_argument = self._check_if_local_argument(chunks[0])
            if is_argument is not None:
                return is_argument
            return None

        # Check for sprite or built-in library
        first, rest = chunks[0], chunks[1:]
        if first in self.sprites:
            return self._check_sprite(first, rest)

        if first in builtin_libraries:
            return _check_library(first, rest)
        return None

    def _check_if_local_argument(self, identifier):
        if self.current_scope == "global":
            return None
        sprite = self.sprites[self.current_scope]
        current_function = sprite["functions"][self.current_function_name]
        if identifier in current_function:
            return "argument"
        return None

    def _check_global_identifier_or_sprite(self, name):
        """Helper to check global variables, functions, or if it's a sprite."""
        if name in self.global_variables:
            return "variable"
        if name in self.global_functions:
            return "function"
        if name in self.sprites:
            return "sprite"
        for function in self.global_functions:
            if name in self.global_functions[function]:
                return "argument"

        return None

    def _check_sprite(self, sprite_name, rest):
        """Recursive check for sprite variables or functions."""
        sprite = self.sprites[sprite_name]
        if len(rest) == 1:
            if rest[0] in sprite["variables"]:
                return "variable"
            if f"{self.current_scope}." + rest[0] in sprite["functions"]:
                return "function"
            if rest[0] in sprite_methods:
                return "method"
        return None

    def parse_block(self, tokens, starting_index):
        # Store the original token stream to restore after block parsing
        original_tokens = self.tokens
        self.tokens = tokens  # Temporarily replace tokens with block's tokens
        self.current_token_index = 0  # Reset index for this block

        instructions = []
        while self.current_token_index < len(self.tokens):
            token = self.current_token()
            token_type = token[0]
            token_value = token[1]
            if token_type == 'KEYWORD':
                if token_value == 'create':
                    raise Exception("Can't create a sprite inside braces!")
                elif token_value == 'define':
                    raise Exception("Can't define a function inside braces!")
                elif token_value == 'var':
                    instructions.append(self.parse_temp_variable())
                elif token_value == "if":
                    instructions.append(self.parse_if_statement())
                elif token_value == "repeat":
                    instructions.append(self.parse_repeat(repeat_type="repeat"))
                elif token_value == "repeat_until":
                    instructions.append(self.parse_repeat(repeat_type="repeat_until"))
            elif token_type == 'ID':
                identifier = self.expect_identifier()

                identifier_type, identifier = self.get_identifier_type(identifier)
                identifier_name = identifier

                # if len(identifier.split(".")) == 2:
                #     identifier_name = self.get_temp_variable_identifier(identifier.split(".")[1])
                #     identifier_type = self.get_identifier_type(identifier_name)
                #
                #     if identifier_type is None:
                #         identifier_name = identifier
                #         identifier_type = self.get_identifier_type(identifier_name)
                #         if identifier_type is None:
                #             raise Exception(f"'{identifier_name}' doesn't exist!")

                if identifier_type == "function":
                    instructions.append(
                        self.parse_function_call(function_name=identifier_name, execution_type="call_block"))

                if identifier_type == "variable":
                    instructions.append(self.parse_assign_variable(variable_name=identifier_name))

                if identifier_type == "method":
                    instructions.append(
                        self.parse_function_call(function_name=identifier_name, execution_type="call_method"))

                self.advance()
                # handle functions or getting variables
            else:
                self.advance()

        # Restore the original tokens and index after parsing the block
        self.tokens = original_tokens
        self.current_token_index = starting_index

        return instructions

    def current_token(self):
        if self.current_token_index < len(self.tokens):
            return self.tokens[self.current_token_index]
        return None

    def advance(self):
        self.current_token_index += 1

    def expect(self, token_type):
        token = self.current_token()

        if token and token[0] == token_type:
            self.advance()
            return token
        raise SyntaxError(f"Expected {token_type}, got {token[0]}")

    def parse_repeat(self, repeat_type):
        self.advance()
        self.expect("LPAREN")
        args = self.parse_args_in()

        if len(args) > 1 or len(args) < 1:
            raise Exception("Invalid repeat expression!")

        self.expect("RPAREN")
        self.expect("LBRACE")
        body = self.parse_body()

        return [repeat_type, args[0], body]

    def parse_assign_variable(self, variable_name):
        self.expect("ASSIGN")
        tokens = self.parse_ongoing_tokens()
        return ["assign", variable_name, tokens]

    def parse_ongoing_tokens(self):
        tokens = []
        while not (self.current_token()[0] == "END" or self.current_token() is None):
            if self.current_token()[0] == "ID":
                identifier = self.expect_identifier()
                self.current_token_index -= 1  # ????

                identifier_type, identifier = self.get_identifier_type(identifier)

                if identifier_type == "variable" or identifier_type == "argument":
                    tokens.append((identifier_type.upper(), identifier))
                else:
                    raise Exception(f"{identifier} isn't a variable!")

            else:
                tokens.append(self.current_token())
            self.advance()
        return tokens

    def expect_identifier(self, last=None):
        token = self.expect("ID")  # Expect the current token to be an ID
        identifier = (last or "") + token[1]  # Start building the identifier string

        # Keep checking for further indexing (i.e., if there's a '.' followed by another ID)
        while self.current_token()[0] == "INDEX":
            self.advance()  # Move past the '.'
            next_token = self.expect("ID")  # Expect another identifier after the '.'
            identifier += "." + next_token[1]  # Concatenate the next part to the identifier

        return identifier  # Return the full identifier (e.g., 'cat.variable1')

    def create_variable(self, name, initial_value=None):
        if initial_value is not None:
            initial_value = remove_quotation_mark(initial_value)

        path = name.split(".")

        if len(path) == 1:
            self.global_variables[
                remove_quotation_mark(name)] = initial_value  # append([remove_quotation_mark(name), initial_value])
        else:
            if path[0] in self.sprites:
                self.sprites[path[0]]["variables"][path[1]] = initial_value
            else:
                raise Exception(f"Couldn't create local variable for '{path[0]}', the sprite doesn't exist!")

    def parse_function_call(self, function_name, execution_type):
        self.expect("LPAREN")
        args = self.parse_args_in()
        self.advance()
        identifier_type = self.get_identifier_type(function_name)
        if identifier_type == "method":
            if self.current_scope != function_name.split(".")[0]:
                raise Exception(f"{function_name} can't be called in '{self.current_scope}' scope!")

        return [execution_type, function_name, args]

    def get_temp_variable_identifier(self, identifier):
        return f"{self.current_function_name} {identifier}"

    def parse_temp_variable(self):
        self.advance()
        identifier = self.expect_identifier()
        split_identifier = identifier.split(".")

        variable_identifier = self.get_temp_variable_identifier(split_identifier[1])
        variable_identifier_split = variable_identifier.split(".")

        if not variable_identifier_split[1] in self.sprites[self.current_scope]:
            self.sprites[self.current_scope]["variables"][variable_identifier_split[1]] = None
        else:
            raise Exception(f"Variable {variable_identifier} already exists!")

        self.expect("ASSIGN")

        return ["assign", variable_identifier, self.parse_ongoing_tokens()]

    def parse_variable(self):
        self.advance()
        variable_name = self.expect_identifier()
        identifier_type = self.get_identifier_type(variable_name)
        if identifier_type == "variable":
            raise Exception(f"There's more than one variable '{variable_name}'!")

        if self.current_token()[0] == "ASSIGN":
            self.advance()
            initial_value = self.current_token()
            if initial_value[0] == "STRING" or initial_value[0] == "NUMBER":
                self.create_variable(name=variable_name, initial_value=initial_value[1])
            else:
                raise Exception(
                    f"'STRING' or 'NUMBER' expected, got {initial_value[0]} when initializing {variable_name}!")
        else:
            self.create_variable(name=variable_name)

    def parse_create(self):
        self.advance()
        token = self.expect("STRING")
        token_value = remove_quotation_mark(token[1])
        self.sprites[token_value] = {
            "variables": {},
            "functions": {},
            "lists": []
        }
        self.advance()

    def parse_args_out(self):
        arguments = []
        while self.current_token()[0] != "RPAREN":
            if self.current_token()[0] == "ID":
                arguments.append(self.current_token())
            self.advance()

            if self.current_token()[0] == "COMMA":
                self.advance()
                continue
            if self.current_token()[0] == "RPAREN":
                continue
            raise Exception("Arguments for function have to be seperated with commas!")

        return arguments

    def parse_args_in(self):
        arguments = []
        current_argument = []
        while self.current_token()[0] != "RPAREN":
            current_token = self.current_token()
            if current_token[0] == "ID":
                identifier = self.expect_identifier()

                identifier_type, identifier = self.get_identifier_type(identifier)

                # if len(identifier.split(".")) == 2:
                #     identifier_name = self.get_temp_variable_identifier(identifier.split(".")[1])
                #     identifier_type = self.get_identifier_type(identifier_name)
                #
                #     if identifier_type == "variable":
                #         identifier = identifier_name
                #
                #     if identifier_type is None:
                #         identifier_name = identifier
                #         identifier_type = self.get_identifier_type(identifier)
                #         if identifier_type is None:
                #             raise Exception(f"'{identifier_name}' doesn't exist!")

                if not (identifier_type == "variable" or identifier_type == "argument"):
                    raise Exception(f"{identifier} is not a variable or argument!")
                self.current_token_index -= 1
                current_argument.append((identifier_type.upper(), identifier))
            if current_token[0] == "STRING":
                current_argument.append(current_token)
            if current_token[0] == "NUMBER":
                current_argument.append(current_token)
            if current_token[0] == "OP":
                current_argument.append(current_token)
            if current_token[0] == "COMPARE":
                current_argument.append(current_token)
            if current_token[0] == "COMMA":
                arguments.append(current_argument)
                current_argument = []
            self.advance()

        arguments.append(current_argument)
        return arguments

    def parse_body(self):
        brace_stack = 1
        tokens_in_between = []

        while True:
            current_token = self.current_token()

            if current_token[0] == "LBRACE":
                brace_stack += 1
            if current_token[0] == "RBRACE":
                brace_stack -= 1

            if brace_stack == 0 and current_token[0] == "RBRACE":
                break

            if current_token is None:
                raise Exception(f"Went out of range, missing closing brace!")

            tokens_in_between.append(current_token)
            self.advance()
        end_index = self.current_token_index

        return self.parse_block(tokens_in_between, starting_index=end_index)

    def parse_define(self):
        self.advance()
        function_name = self.expect_identifier()
        self.expect("LPAREN")
        args = self.parse_args_out()
        self.expect("RPAREN")
        self.expect("LBRACE")

        args = [arg[1] for arg in args]

        split_identifier = function_name.split(".")
        identifier_length = len(split_identifier)

        if identifier_length == 2:
            self.current_scope = split_identifier[0]

        self.current_function_name = function_name

        identifier_type = self.get_identifier_type(function_name)
        if identifier_type == "variable":
            raise Exception(f"Function '{function_name}' can't have the same name as an already existing variable!")
        if identifier_type == "function":
            raise Exception(f"Function '{function_name}' already exists!")
        if identifier_type == "sprite":
            raise Exception(f"Function '{function_name}' can't have the same name as an already existing sprite!")

        if identifier_length == 1:
            self.global_functions[split_identifier[0]] = args

        if identifier_length == 2:
            if self.sprites[split_identifier[0]] is None:
                raise Exception(f"Can't create '{function_name}', sprite doesn't exist!")
            self.sprites[split_identifier[0]]["functions"][function_name] = args

        body = self.parse_body()

        self.current_scope = "global"

        return ["function", function_name, args, body]

    def parse_expression(self):
        # Simplified expression parsing; extend as needed
        expression_tokens = []

        while self.current_token() is not None:
            current_token = self.current_token()
            if current_token[0] == "RPAREN":
                self.advance()
                break
            expression_tokens.append(self.current_token())
            self.advance()

        return expression_tokens

    def parse_if_statement(self):
        self.advance()  # Skip 'if'
        self.expect('LPAREN')  # Expect '('
        condition = self.parse_expression()  # Parse the condition expression
        self.expect('LBRACE')  # Expect '{'
        body = self.parse_body()  # Parse the body of the if statement

        return ['if', condition, body]
