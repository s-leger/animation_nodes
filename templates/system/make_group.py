import bpy
from ... base_types.template import Template

class MakeGroupTemplateOperator(bpy.types.Operator, Template):
    bl_idname = "an.make_group_template_operator"
    bl_label = "Make Group"

    def insert(self):
        nodes = self.selectedNodes
