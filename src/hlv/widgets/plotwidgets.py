import holoviews as hv
import panel as pn
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QGridLayout, QWidget


class HoloVizWidget(QWidget):
    def __init__(self, viewer, model):
        self.embedding_plot = None
        self.sample_selector = None
        hv.extension("bokeh")
        super().__init__()
        self.viewer = viewer
        self.model = model
        self.setLayout(QGridLayout())
        self._current_selection = []
        self.setup_panel()
        self.browser = QWebEngineView()
        self.browser.load(QUrl("http://localhost:8081"))

        self.layout().addWidget(self.browser)

        self._last_indices = []

    def setup_panel(self):
        pn.config.sizing_mode = "stretch_width"
        self.panel = pn.pane.HoloViews()
        self.setup_csv_dropdown()
        self.panel.servable(title="basic plot")
        pn.serve(
            self.panel,
            port=8081,
            websocket_origin=["*"],
            show=False,
            threaded=True,
        )

    def setup_csv_dropdown(self):
        self.sample_selector = pn.widgets.Select(
            name="Select CSV",
            options=list(self.model.path_csv_mapper.keys()),
            value=list(self.model.path_csv_mapper.keys())[0],
        )
        self.sample_selector.param.watch(self.update_sample_plot, "value")
        df = self.model.path_csv_mapper[
            list(self.model.path_csv_mapper.keys())[0]
        ]
        self.panel.layout = pn.Column(
            self.sample_selector,
            hv.Points(df).opts(responsive=True),
        )
        self.embedding_plot = self.panel.layout[1]

    def update_sample_plot(self, event):
        if event.type == "changed":
            df = self.model.path_csv_mapper[event.new]
            # TODO: check whether instead of creating new plot we can just overwrite the Column data source
            self.panel.layout[1] = hv.Points(df).opts(responsive=True)
            self.embedding_plot = self.panel.layout[1]
