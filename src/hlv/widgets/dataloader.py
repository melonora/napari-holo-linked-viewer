from pathlib import Path

import pandas as pd
from napari import Viewer
from napari.utils.history import get_open_history, update_open_history
from napari.utils.notifications import NotificationSeverity
from qtpy.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QWidget,
)

from hlv.model.datamodel import DataModel
from hlv.utils.utils import napari_notification
from hlv.widgets.plotwidgets import HoloVizWidget


class DataLoaderWidget(QWidget):
    """Sample widget for loading required data."""

    def __init__(
        self, napari_viewer: Viewer, model: DataModel | None = None
    ) -> None:
        """
        Create the QWidget visuals.

        This widget sets up the QtWidget elements used to determine what the input is that the user wants to use
        for cell gating. It also connects these elements to their appropriate callback functions.

        Parameters
        ----------
        viewer : napari.Viewer
            The napari Viewer instance.
        model : DataModel | None
            The data model dataclass. If provided, this means that the plugin is used by means of a CLI to be
            implemented.

        """
        super().__init__()
        self._holoviz_widget = None
        self._viewer = napari_viewer
        self._model = DataModel() if model is None else model
        self.setLayout(QGridLayout())
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # object, int row, int column, int rowSpan = 1, int columnSpan = 1

        # Open sample directory dialog
        self.load_csv_button = QPushButton("Load csvs")
        self.load_csv_button.clicked.connect(self._open_sample_dialog)
        self.layout().addWidget(self.load_csv_button, 0, 0, 1, 2)

        filter_label = QLabel("Only use columns for axis with prefix")
        self.filter_field = QLineEdit("UMAP", placeholderText="UMAP")
        self.filter_field.editingFinished.connect(self._update_filter)
        self.layout().addWidget(filter_label, 1, 0, 1, 1)
        self.layout().addWidget(self.filter_field, 2, 0, 1, 2)

        # Button to start validating all the input
        self.validate_button = QPushButton("Validate input and plot")
        self.validate_button.clicked.connect(self.validate)
        self.layout().addWidget(self.validate_button, 3, 0, 1, 2)

        self.model.events.csv_paths.connect(self.load_csvs)

    @property
    def model(self) -> DataModel:
        return self._model

    @property
    def viewer(self) -> Viewer:
        return self._viewer

    def _open_sample_dialog(self, folder: str | None = None):
        """Open directory file dialog for regionprop directory."""
        if not folder:
            folder = self._dir_dialog()

        if isinstance(folder, str) and folder != "":
            self.model.csv_paths = Path(folder)
            update_open_history(folder)

    def _dir_dialog(self):
        """Open dialog for a user to pass on a directory."""
        dlg = QFileDialog()
        hist = get_open_history()
        dlg.setHistory(hist)
        return dlg.getExistingDirectory(
            self,
            "select folder",
            hist[0],
            QFileDialog.Options(),
        )

    def load_csvs(self):
        csv_dict = {}
        for path in self.model.csv_paths:
            csv_dict[path.stem] = pd.read_csv(path)
        self.model.path_csv_mapper = csv_dict
        self.set_axis_columns()

    def set_axis_columns(self):
        for df in self.model.path_csv_mapper.values():
            self.model.axis_columns = df.columns

    def _update_filter(self):
        """Update marker filter upon text change of the filter field widget."""
        self.model.col_string_filter = self.filter_field.text()

    def validate(self):
        if self.model.col_string_filter != "":
            cols = [
                col
                for col in self.model.axis_columns
                if col.startswith(self.model.col_string_filter)
            ]
            if len(cols) >= 2:
                self.model.axis_columns = cols

        if len(cols := self.model.axis_columns) < 2:
            napari_notification(
                "After filtering on prefix, there are not enough columns (2 required). "
                f"Got {len(cols)} columns.",
                severity=NotificationSeverity.ERROR,
            )

        self._holoviz_widget = HoloVizWidget(self.viewer, self.model)
        self.viewer.window.add_dock_widget(
            self._holoviz_widget,
            name="Holoviews plotter",
            area="right",
            menu=self._viewer.window.window_menu,
            tabify=True,
        )
