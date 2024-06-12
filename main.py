import zipper
from scratch_utils import BlockChain, OPCODES, Project, BUILTIN_COSTUMES


def main():
    chain = BlockChain()

    chain.add_block(OPCODES.EVENT_WHENFLAGCLICKED)
    chain.add_block(OPCODES.MOTION_MOVESTEPS, [100])
    chain.add_block(OPCODES.MOTION_TURNRIGHT, [90])
    chain.add_block(OPCODES.MOTION_MOVESTEPS, [50])

    new_project = Project()
    new_project.create_sprite("Cat", BUILTIN_COSTUMES.DEFAULT_CAT)
    new_project.add_block_chain("Cat", chain)

    new_project.save()
    zipper.build_project()


if __name__ == '__main__':
    main()
