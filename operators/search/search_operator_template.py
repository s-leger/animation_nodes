import bpy
from . text_line_handler import TextLineHandler

class SearchOperatorTemplate:

    # Replace in real implementation

    def getSearchItems(self):
        raise NotImplementedError()

    def getSpace(self):
        raise NotImplementedError()


    # Internals

    def invoke(self, context, event):
        self.textLine = TextLineHandler()
        self.items = self.getSearchItems()
        self.drawHandler = self.getSpace().draw_handler_add(self.drawCallback, (), "WINDOW", "POST_PIXEL")
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        self.textLine.handleEvent(event)

        if event.type in {"RIGHTMOUSE", "ESC"}:
            return self.finish()

        context.area.tag_redraw()
        return {"RUNNING_MODAL"}

    def finish(self):
        self.getSpace().draw_handler_remove(self.drawHandler, "WINDOW")
        bpy.context.area.tag_redraw()
        return {"CANCELLED"}


    # Drawing

    def drawCallback(self):
        drawer = TextLineDrawer(self.textLine.text, (50, 50), self.textLine.cursor, self.textLine.getSelection())
        drawer.draw()

import blf
from bgl import *
from mathutils import Vector
from ... graphics.rectangle import Rectangle
font = 1

class TextLineDrawer:
    def __init__(self, text, position, cursor = 0, selection = (0, 0)):
        self.text = text
        self.position = Vector(position)
        self.cursor = cursor
        self.selection = selection

    def draw(self):
        blf.size(font, 20, 72)

        # Measure Text

        totalWidth = blf.dimensions(font, self.text)[0]
        startToCursorPixels = blf.dimensions(font, self.text[:self.cursor])[0]
        startToSelectionPixels = blf.dimensions(font, self.text[:self.selection[0]])[0]
        selectionWidthPixels = blf.dimensions(font, self.text[self.selection[0]:self.selection[1]])[0]
        startToSelectionEndPixels = startToSelectionPixels + selectionWidthPixels

        top = blf.dimensions(font, "l")[1] + 4
        bottom = blf.dimensions(font, "lg")[1] - top + 6
        theme = getCurrentTheme()
        menuBackTheme = theme.user_interface.wcol_menu_back

        # Draw Background

        background = Rectangle(self.position.x, self.position.y + top,
                               self.position.x + totalWidth, self.position.y - bottom)
        background.color = menuBackTheme.inner_sel
        background.draw()

        # Draw Selection

        selectionBackgroud = Rectangle(self.position.x + startToSelectionPixels, self.position.y + top,
                                       self.position.x + startToSelectionEndPixels, self.position.y - bottom)
        selectionBackgroud.color = (0.3, 0.3, 0.7, 0.4)
        selectionBackgroud.borderThickness = 1
        selectionBackgroud.borderColor = (0.3, 0.3, 0.7, 0.9)
        selectionBackgroud.draw()

        # Draw Text

        blf.position(font, self.position.x, self.position.y, 0)
        glColor4f(*(list(menuBackTheme.text_sel) + [1]))
        blf.draw(font, self.text)

        # Draw Cursor

        glLineWidth(1)
        glBegin(GL_LINES)
        glVertex2f(self.position.x + startToCursorPixels, self.position.y + top)
        glVertex2f(self.position.x + startToCursorPixels, self.position.y - bottom)
        glEnd()




def getCurrentTheme():
    return bpy.context.user_preferences.themes[0]
