from panda3d.core import LVecBase4f

LIGHT_ZERO = LVecBase4f(-0.96104145, -0.078606814, -0.2593495, 1.0)
LIGHT_ONE = LVecBase4f(-0.26765957, -0.95667744, 0.100838766, 1.0)

LIGHT_ZERO_ITEM = LVecBase4f(-0.22218964, 0.17124468, 0.9583053, 1.0)
LIGHT_ONE_ITEM = LVecBase4f(-0.21469395, 0.9703869, 0.09642491, 1.0)


def get_light_zero_vec():
    return LIGHT_ZERO


def get_light_one_vec():
    return LIGHT_ONE


def get_light_zero_item_vec():
    return LIGHT_ZERO_ITEM


def get_light_one_item_vec():
    return LIGHT_ONE_ITEM
