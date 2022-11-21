"""
    abstract window providing the same interface
"""

from typing import Optional, List, Tuple

from overrides import override

from PySide6.QtCore import Slot, Qt  # pylint: disable=import-error
from PySide6.QtGui import QCloseEvent  # pylint: disable=import-error
from PySide6.QtWidgets import (  # pylint: disable=import-error
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QMessageBox,
    QScrollArea,
)

from IPTables_Guide.view.custom_table_widget import CustomTableWidget
from IPTables_Guide.view.gui_utils import log_gui


class AbstractTableWindow(QMainWindow):
    """
    Window representing a table
    """

    def __init__(
        self,
        table_name: str,
        row_types: List[Tuple[str, type]],
        parent: Optional[QWidget] = None,
    ) -> None:
        """ """
        super().__init__(parent)
        self.setCentralWidget(QWidget(self))
        self.resize(600, 400)
        self.main_layout = QHBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        self.menu_line = QWidget(self.centralWidget())
        self.menu_line.setFixedWidth(180)

        self.table = CustomTableWidget(
            row_types,
            self.centralWidget(),
        )
        self.scroll_layout = QVBoxLayout()
        self.scroll_widget = QWidget(self.centralWidget())
        self.scroll_layout.addWidget(self.table)
        self.scroll_layout.insertStretch(-1)
        self.scroll_widget.setLayout(self.scroll_layout)

        self.scroll_area = QScrollArea(self.centralWidget())
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn) # type: ignore
        self.scroll_area.setWidgetResizable(True)

        self.main_layout.addWidget(self.menu_line)
        self.table_layout = QVBoxLayout()
        # TODO CHAIN = selected radiobutton chain name
        self.table_layout.addWidget(
            QLabel(
                "sudo iptables -L " + "CHAIN" + " -t " + table_name,
                self.centralWidget(),
            )
        )
        self.table_layout.addWidget(self.scroll_area)
        self.table_layout.insertStretch(-1)
        self.main_layout.addLayout(self.table_layout)

        for i in range(self.table_layout.count()):
            log_gui(self.table_layout.itemAt(i)) # type: ignore
        self.table_layout.removeItem(self.table_layout.itemAt(2))

        self.menu_line.setLayout(QVBoxLayout())

    def _get_selected_indices(self) -> List[int]:
        return [
            i
            for i, w in enumerate(self.table.get_column("select"))
            if w.isChecked()  # type: ignore
        ]

    @Slot()
    def append_row(self):
        """
        Append a row to the end of the table
        """
        # TODO call API first and wait for its signal
        self.table.add_row()
        self._set_row(len(self.table) - 1)

    @Slot()
    def insert_row(self):
        """
        Append a row to the end of the table
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) != 1:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message")
            msg_box.setText("Insert is only enabled for exactly one row selected")
            msg_box.exec()
            return
        # TODO call API first and wait for its signal
        self.table.insert_row(inds[0])
        self._set_row(inds[0])

    @Slot()
    def delete_row(self):
        """
        remove rows from table
        """
        inds: List[int] = self._get_selected_indices()
        if len(inds) == 0:
            msg_box = QMessageBox()
            msg_box.setWindowTitle("Message")
            msg_box.setText("No selected items")
            msg_box.exec()
            return
        # TODO call API first and wait for its signal
        del self.table[self._get_selected_indices()]

    def _set_row(self, ind: int) -> None:  # pylint: disable-all
        ...

    @override
    def closeEvent(self, event: QCloseEvent) -> None:  # pylint: disable=invalid-name
        """
        handling close event
        """
        assert log_gui(f"{type(self)} Closed")
        super().closeEvent(event)
        self.deleteLater()
