import zipper
import Scratch


def main():
    project = Scratch.Project()
    sprite = Scratch.Sprite("Cat")

    block_stack = Scratch.BlockStack()

    block1 = Scratch.Block(opcode="event_whenflagclicked")
    block2 = Scratch.Block(opcode="motion_movesteps", args={
        "STEPS": [
            1,
            [
                4,
                "25"
            ]
        ]
    })

    block_stack.add_block(block1)
    block_stack.add_block(block2)

    sprite.set_block_stack(block_stack)

    project.add_sprite(sprite)

    project.build_project()
    zipper.build_sb3()


if __name__ == '__main__':
    main()
