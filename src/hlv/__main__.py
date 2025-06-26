def main():
    from qtpy.QtQuick import QQuickWindow, QSGRendererInterface

    QQuickWindow.setGraphicsApi(QSGRendererInterface.GraphicsApi.OpenGL)

    import napari

    viewer = napari.Viewer()
    viewer.window.add_plugin_dock_widget("holo-linked-viewer")
    napari.run()
