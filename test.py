import folium
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView

def create_map():
    m = folium.Map(location=[47, 1], zoom_start=6)

    folium.Marker(
        location=[47.2, 1.5],
        popup="Commune conforme",
        icon=folium.Icon(color="green")
    ).add_to(m)

    m.save("map.html")



class MainWindow(QMainWindow):
    def init(self):
        super().init()
        self.setWindowTitle("Supervision Qualité de l'Eau")
        self.browser = QWebEngineView()
        self.browser.load(QUrl.fromLocalFile(
            "map.html"
        ))

        self.setCentralWidget(self.browser)


if __name__ == "__main__":
    create_map()

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())