import bpy

maxIndex = 1000

class TextLineHandler:
    def __init__(self):
        self._text = ""
        self.selection = TextLineSelection()

    def handleEvent(self, event):
        if event.ascii:
            self.write(event.ascii)

        if event.value != "PRESS": return

        if event.type == "LEFT_ARROW": self.selection.moveCursor(-1, event.shift)
        if event.type == "RIGHT_ARROW": self.selection.moveCursor(1, event.shift)
        if event.type == "END": self.selection.moveCursor(maxIndex, event.shift)
        if event.type == "HOME": self.selection.moveCursor(-maxIndex, event.shift)
        if event.type == "A" and event.ctrl: self.selection.setSelection(0, maxIndex)

        if event.type == "C" and event.ctrl: bpy.context.window_manager.clipboard = self.selectedText
        if event.type == "V" and event.ctrl: self.write(bpy.context.window_manager.clipboard)

        if self.textInSelection:
            if event.type in ("DEL", "BACK_SPACE"): self.removeTextInSelection()
        else:
            if event.type == "DEL": self.removeAfterCursor(1)
            if event.type == "BACK_SPACE": self.deleteBeforeCursor(1)

        self.selection.updateToLength(len(self.text))

    def write(self, text):
        self.removeTextInSelection()
        self.text = self.textBeforeCursor + text + self.textAfterCursor
        self.selection.moveCursor(len(text))

    def deleteBeforeCursor(self, amount):
        before = self.textBeforeCursor[:-amount]
        self.text = before + self.textAfterCursor
        self.selection.setCursor(len(before))

    def removeAfterCursor(self, amount):
        self.text = self.textBeforeCursor + self.textAfterCursor[amount:]

    def removeTextInSelection(self):
        self.text = self.textBeforeSelection + self.textAfterSelection
        self.selection.resetSelection()


    def getSelection(self):
        return (self.selection.start, self.selection.end)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.selection.updateToLength(len(self._text))

    @property
    def textBeforeSelection(self):
        return self.text[:self.selection.start]

    @property
    def textInSelection(self):
        return self.text[self.selection.start:self.selection.end]

    @property
    def selectedText(self):
        return self.textInSelection

    @property
    def textAfterSelection(self):
        return self.text[self.selection.end:]

    @property
    def textBeforeCursor(self):
        return self.text[:self.selection.cursor]

    @property
    def textAfterCursor(self):
        return self.text[self.selection.cursor:]

    @property
    def cursor(self):
        return self.selection.cursor


class TextLineSelection:
    def __init__(self):
        self._cursor = 0
        self._selectionEnd = 0

    def moveCursor(self, amount, select = False):
        self.setCursor(self.cursor + amount, select)

    def setCursor(self, position, select = False):
        self.cursor = position
        if not select: self.resetSelection()

    def setSelection(self, start, end):
        self.selectionEnd = start
        self.cursor = end

    def resetSelection(self):
        self.selectionEnd = self.cursor

    def updateToLength(self, length):
        self.cursor = min(length, self.cursor)
        self.selectionEnd = min(length, self.selectionEnd)

    @property
    def start(self):
        return min(self.cursor, self.selectionEnd)

    @property
    def end(self):
        return max(self.cursor, self.selectionEnd)

    @property
    def length(self):
        return abs(self.cursor - self.selectionEnd)

    @property
    def cursor(self):
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = max(0, value)

    @property
    def selectionEnd(self):
        return self._selectionEnd

    @selectionEnd.setter
    def selectionEnd(self, value):
        self._selectionEnd = max(0, value)
