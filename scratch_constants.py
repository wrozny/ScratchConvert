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
