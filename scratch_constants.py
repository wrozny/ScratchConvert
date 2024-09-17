from enum import Enum


class Opcodes(Enum):
    EVENT_WHENFLAGCLICKED = "event_whenflagclicked"
    MOTION_MOVESTEPS = "motion_movesteps"

    DATA_SETVARIABLETO = "data_setvariableto"

    PROCEDURES_DEFINITION = "procedures_definition"
    PROCEDURES_PROTOTYPE = "procedures_prototype"

    CONTROL_IF = "control_if"
    CONTROL_FOREVER = "control_forever"

    LOOKS_SAY = "looks_say"

    OPERATOR_ADD = "operator_add"
    OPERATOR_SUBSTRACT = "operator_subtract"
    OPERATOR_MULTIPLY = "operator_multiply"
    OPERATOR_DIVIDE = "operator_divide"

    OPERATOR_GT = "operator_gt"
    OPERATOR_LT = "operator_lt"
    OPERATOR_EQUALS = "operator_equals"

    OPERATOR_AND = "operator_and"
    OPERATOR_OR = "operator_or"
    OPERATOR_NOT = "operator_not"

    OPERATOR_JOIN = "operator_join"


method_to_opcode_map = {
    "move_steps": Opcodes.MOTION_MOVESTEPS.value,
    "say": Opcodes.LOOKS_SAY.value
}

opcode_to_input_name_map = {
    Opcodes.OPERATOR_ADD.value: "NUM",
    Opcodes.OPERATOR_SUBSTRACT.value: "NUM",
    Opcodes.OPERATOR_MULTIPLY.value: "NUM",
    Opcodes.OPERATOR_DIVIDE.value: "NUM",

    Opcodes.OPERATOR_GT.value: "OPERAND",
    Opcodes.OPERATOR_LT.value: "OPERAND",
    Opcodes.OPERATOR_EQUALS.value: "OPERAND",

    Opcodes.OPERATOR_JOIN.value: "STRING",

    Opcodes.LOOKS_SAY.value: "MESSAGE"
}

symbol_to_opcode_map = {
    "+": Opcodes.OPERATOR_ADD.value,
    "-": Opcodes.OPERATOR_SUBSTRACT.value,
    "*": Opcodes.OPERATOR_MULTIPLY.value,
    "/": Opcodes.OPERATOR_DIVIDE.value,

    ">": Opcodes.OPERATOR_GT.value,
    "<": Opcodes.OPERATOR_LT.value,
    "==": Opcodes.OPERATOR_EQUALS.value,
    "..": Opcodes.OPERATOR_JOIN.value
}


class Inputs(Enum):
    DIRECT_INPUT = 1
    STATEMENT_RESULT = 2
    BLOCK_REFERENCE = 3
    SHADOW_INPUT = 4
    PLAIN_TEXT = 10
    VARIABLE_INPUT = 12
    ARGUMENT = 13


META = {
    "semver": "3.0.0",
    "vm": "0.2.0-prerelease.20220222132735",
    "agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Scratch/3.29.1 "
             "Chrome/94.0.4606.81 Electron/15.3.1 Safari/537.36"
}

PROJECT_BASE = {
    "targets": [],
    "monitors": [],
    "extensions": [],
    "meta": META
}

DEFAULT_STAGE = {
    "isStage": True,
    "name": "Stage",
    "variables": {},
    "lists": {},
    "broadcasts": {},
    "blocks": {},
    "comments": {},
    "currentCostume": 0,
    "costumes": [
        {
            "assetId": "cd21514d0531fdffb22204e0ec5ed84a",
            "name": "Backdrop",
            "md5ext": "cd21514d0531fdffb22204e0ec5ed84a.svg",
            "dataFormat": "svg",
            "rotationCenterX": 240,
            "rotationCenterY": 180
        }
    ],
    "sounds": [],
    "volume": 100,
    "layerOrder": 0,
    "tempo": 60,
    "videoTransparency": 50,
    "videoState": "on",
    "textToSpeechLanguage": None
}

SPRITE_BASE = {
    "isStage": False,
    "name": "Sprite",
    "variables": {},
    "lists": {},
    "broadcasts": {},
    "blocks": {},
    "comments": {},
    "currentCostume": 0,
    "costumes": [
        {
            "assetId": "bcf454acf82e4504149f7ffe07081dbc",
            "name": "Costume1",
            "bitmapResolution": 1,
            "md5ext": "bcf454acf82e4504149f7ffe07081dbc.svg",
            "dataFormat": "svg",
            "rotationCenterX": 48,
            "rotationCenterY": 50
        },
    ],
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

BLOCK_BASE = {
    "opcode": "event_whenflagclicked",
    "next": None,
    "parent": None,
    "inputs": {},
    "fields": {},
    "shadow": False,
    "topLevel": False
}
