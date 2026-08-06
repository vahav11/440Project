from PyQt6.QtCore import Qt


class KeyNavMixin:
    """Adds keyboard navigation to a page.

    Enter  -> move to the next field, or press the submit button on the last one
    Up     -> move to the previous field
    Down   -> move to the next field
    """

    def setup_key_navigation(self, fields, submit_button):
        self._fields = fields

        for i, field in enumerate(fields):
            if i < len(fields) - 1:
                field.returnPressed.connect(
                    lambda nxt=fields[i + 1]: nxt.setFocus()
                )
            else:
                field.returnPressed.connect(submit_button.click)

    def keyPressEvent(self, event):
        key = event.key()

        if key in (Qt.Key.Key_Up, Qt.Key.Key_Down):
            current = self.focusWidget()

            if current in getattr(self, "_fields", []):
                i = self._fields.index(current)

                if key == Qt.Key.Key_Down and i < len(self._fields) - 1:
                    self._fields[i + 1].setFocus()
                elif key == Qt.Key.Key_Up and i > 0:
                    self._fields[i - 1].setFocus()

                return

        super().keyPressEvent(event)
