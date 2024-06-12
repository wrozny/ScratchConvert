import json
import os

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


class BUILTIN_COSTUMES:
    DEFAULT_BACKDROP = {
        "assetId": "cd21514d0531fdffb22204e0ec5ed84a",
        "name": "DEFAULT_BACKDROP",
        "md5ext": "cd21514d0531fdffb22204e0ec5ed84a.svg",
        "dataFormat": "svg",
        "rotationCenterX": 240,
        "rotationCenterY": 180
    }
    DEFAULT_CAT = {
        "assetId": "bcf454acf82e4504149f7ffe07081dbc",
        "name": "DEFAULT_CAT",
        "bitmapResolution": 1,
        "md5ext": "bcf454acf82e4504149f7ffe07081dbc.svg",
        "dataFormat": "svg",
        "rotationCenterX": 48,
        "rotationCenterY": 50
    }


class OPCODES:
    EVENT_WHENFLAGCLICKED = "event_whenflagclicked"

    MOTION_MOVESTEPS = "motion_movesteps"
    MOTION_TURNRIGHT = "motion_turnright"

    OPERATOR_ADD = "operator_add"
    OPERATOR_SUBTRACT = "operator_subtract"
    OPERATOR_MULTIPLY = "operator_multiply"
    OPERATOR_DIVIDE = "operator_divide"


input_values = {
    OPCODES.EVENT_WHENFLAGCLICKED: None,
    OPCODES.MOTION_TURNRIGHT: "DEGREES",
    OPCODES.MOTION_MOVESTEPS: "STEPS",

    OPCODES.OPERATOR_ADD: "NUM",
    OPCODES.OPERATOR_SUBTRACT: "NUM",
    OPCODES.OPERATOR_MULTIPLY: "NUM",
    OPCODES.OPERATOR_DIVIDE: "NUM",
}

DEFAULT_BACKDROP = {
    "isStage": True,
    "name": "Stage",
    "currentCostume": 0,
    "variables": {},
    "broadcasts": {},
    "blocks": {},
    "comments": {},
    "costumes": [
        BUILTIN_COSTUMES.DEFAULT_BACKDROP
    ],
    "sounds": [],
    "volume": 100,
    "layerOrder": 0,
    "tempo": 60,
    "videoTransparency": 50,
    "videoState": "on",
    "textToSpeechLanguage": None
}

DEFAULT_META = {
    "semver": "3.0.0",
    "vm": "0.2.0-prerelease.20220222132735",
    "agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Scratch/3.29.1 Chrome/94.0.4606.81 Electron/15.3.1 Safari/537.36"
}


class Block:
    def __init__(self, opcode, id, args):
        self.opcode = opcode
        self.args = args
        self.name = f"{opcode}_{id}"

    def translate_args(self):
        if self.args is None:
            return {}

        output = {}
        for i, arg in enumerate(self.args):
            output[f"{input_values[self.opcode]}"] = [1, [
                4, arg
            ]]
        return output

    def build(self, last, next):
        content = {
            "opcode": self.opcode,
            "next": next,
            "parent": last,
            "inputs": self.translate_args(),
            "fields": {},
            "shadow": False,
            "topLevel": last is None,
        }
        # if at top level then assign position
        if last is None:
            content["x"] = 0
            content["y"] = 0

        return self.name, content


class BlockChain:
    def __init__(self):
        self.blocks = []
        self.current_id = 0

    def add_block(self, opcode, args=None):
        new_block = Block(opcode=opcode, args=args, id=self.current_id)
        self.blocks.append(new_block)
        self.current_id += 1

    def generate(self):
        output = {}
        previous_block_name = None

        for block_id, block in enumerate(self.blocks):
            next_block_name = None

            try:
                next_block_name = self.blocks[block_id + 1].name
            except IndexError:
                pass

            name, content = block.build(last=previous_block_name, next=next_block_name)

            output[name] = content

            previous_block_name = name

        return output


class Project:
    def __init__(self):
        self.block_chains = []
        self.project = {
            "targets": [
                DEFAULT_BACKDROP
            ],
            "monitors": [],
            "extensions": [],
            "meta": DEFAULT_META
        }

    def create_sprite(self, name, sprite_data):
        sprite = {
            "isStage": False,
            "name": name,
            "variables": {},
            "lists": {},
            "broadcasts": {},
            "blocks": {},
            "comments": {},
            "currentCostume": 0,
            "costumes": [sprite_data],
            "sounds": [],
            "volume": 100,
            "layerOrder": 1,
            "visible": True,
            "x": 0,
            "y": 0,
            "size": 100,
            "direction": 90,
            "draggable": False,
            "rotationStyle": "all around"
        }
        self.project["targets"].append(sprite)

    def add_block_chain(self, sprite_name, block_chain):
        sprite_found = False
        for index, sprite in enumerate(self.project["targets"]):
            if not sprite["name"] == sprite_name:
                continue
            sprite_found = True
            break

        if not sprite_found:
            raise Exception("Sprite not found!")

        self.block_chains.append(
            (sprite_name, block_chain)
        )

    def save(self):
        build_dir = os.path.join(SCRIPT_PATH, "build")
        project_dir = os.path.join(build_dir, "project")

        if not os.path.exists(project_dir):
            os.makedirs(project_dir)

        for block_chain_data in self.block_chains:
            for sprite in self.project["targets"]:
                if sprite["name"] != block_chain_data[0]:
                    continue

                generated_block_chain = block_chain_data[1].generate()

                for block_name, block_data in generated_block_chain.items():
                    sprite["blocks"][block_name] = block_data

                break

        with open(os.path.join(project_dir, "project.json"), "w") as output:
            json_output = json.dumps(self.project)
            output.write(json_output)
