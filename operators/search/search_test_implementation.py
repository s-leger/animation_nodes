import bpy
from . search_operator_template import SearchOperatorTemplate

class SearchTestImplementation(bpy.types.Operator, SearchOperatorTemplate):
    bl_idname = "an.search_test_implementation"
    bl_label = "Search Test Implementation"

    def getSpace(self):
        return bpy.types.SpaceNodeEditor

    def getSearchItems(self):
        return ["Hello World", "Foo", "Bar", "Another Test"]
