import holoviews as hv
import panel as pn
from qtpy.QtCore import QUrl
from qtpy.QtWebEngineWidgets import QWebEngineView
from qtpy.QtWidgets import QGridLayout, QWidget


class HoloVizWidget(QWidget):
    def __init__(self, viewer, model):
        hv.extension("bokeh")
        super().__init__()
        self.viewer = viewer
        self.model = model
        self.setLayout(QGridLayout())
        self._current_selection = []
        self.setup_panel()
        self.browser = QWebEngineView()
        self.browser.load(QUrl("http://localhost:80"))

        self.layout().addWidget(self.browser)

        self._last_indices = []
        # self.timer = QTimer()
        # self.timer.timeout.connect(self._update_on_stream_selection)
        # self.timer.start(300)  # check every 300 ms

    def setup_panel(self):
        pn.config.sizing_mode = "stretch_width"
        self.panel = pn.pane.HoloViews()
        self.panel.servable(title="basic plot")
        pn.serve(
            self.panel,
            port=80,
            websocket_origin=["*"],
            show=False,
            threaded=True,
        )
