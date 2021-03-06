import bpy
from bpy.props import *
from bpy.types import Node, NodeSocket
from arm.logicnode.arm_nodes import *

class OnKeyboardNode(Node, ArmLogicTreeNode):
    '''On keyboard node'''
    bl_idname = 'LNOnKeyboardNode'
    bl_label = 'On Keyboard'
    bl_icon = 'CURVE_PATH'

    property0 = EnumProperty(
        items = [('Down', 'Down', 'Down'),
                 ('Started', 'Started', 'Started'),
                 ('Released', 'Released', 'Released')],
        name='', default='Started')
    
    property1 = EnumProperty(
        items = [('a', 'a', 'a'),
                 ('b', 'b', 'b'),
                 ('c', 'c', 'c'),
                 ('d', 'd', 'd'),
                 ('e', 'e', 'e'),
                 ('f', 'f', 'f'),
                 ('g', 'g', 'g'),
                 ('h', 'h', 'h'),
                 ('i', 'i', 'i'),
                 ('j', 'j', 'j'),
                 ('k', 'k', 'k'),
                 ('l', 'l', 'l'),
                 ('m', 'm', 'm'),
                 ('n', 'n', 'n'),
                 ('o', 'o', 'o'),
                 ('p', 'p', 'p'),
                 ('q', 'q', 'q'),
                 ('r', 'r', 'r'),
                 ('s', 's', 's'),
                 ('t', 't', 't'),
                 ('u', 'u', 'u'),
                 ('v', 'v', 'v'),
                 ('w', 'w', 'w'),
                 ('x', 'x', 'x'),
                 ('y', 'y', 'y'),
                 ('z', 'z', 'z'),
                 ('0', '0', '0'),
                 ('1', '1', '1'),
                 ('2', '2', '2'),
                 ('3', '3', '3'),
                 ('4', '4', '4'),
                 ('5', '5', '5'),
                 ('6', '6', '6'),
                 ('7', '7', '7'),
                 ('8', '8', '8'),
                 ('9', '9', '9'),
                 ('.', '.', '.'),
                 (',', ',', ','),
                 ('space', 'space', 'space'),
                 ('backspace', 'backspace', 'backspace'),
                 ('tab', 'tab', 'tab'),
                 ('enter', 'enter', 'enter'),
                 ('shift', 'shift', 'shift'),
                 ('ctrl', 'ctrl', 'ctrl'),
                 ('alt', 'alt', 'alt'),
                 ('esc', 'esc', 'esc'),
                 ('del', 'del', 'del'),
                 ('back', 'back', 'back'),
                 ('up', 'up', 'up'),
                 ('right', 'right', 'right'),
                 ('left', 'left', 'left'),
                 ('down', 'down', 'down'),],
        name='', default='space')

    def init(self, context):
        self.outputs.new('ArmNodeSocketAction', 'Out')

    def draw_buttons(self, context, layout):
        layout.prop(self, 'property0')
        layout.prop(self, 'property1')

add_node(OnKeyboardNode, category='Input')
