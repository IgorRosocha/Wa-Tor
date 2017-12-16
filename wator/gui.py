from PyQt5 import QtWidgets, QtGui, QtCore, QtSvg, uic
import numpy
from wator import WaTor
import time


CELL_SIZE = 32

FISH_PATH = 'wator/static/pictures/fish.svg'
SHARK_PATH = 'wator/static/pictures/shark.svg'
WATER_PATH = 'wator/static/pictures/water.svg'


SVG_FISH = QtSvg.QSvgRenderer(FISH_PATH)
SVG_SHARK = QtSvg.QSvgRenderer(SHARK_PATH)
SVG_WATER = QtSvg.QSvgRenderer(WATER_PATH)

VALUE_ROLE = QtCore.Qt.UserRole


class GridWidget(QtWidgets.QWidget):
    def __init__(self, array, energy):
        super().__init__()
        self.array = array
        self.energy = energy
        self.CELL_SIZE = 32
        size = self.logical_to_pixels(*array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def mousePressEvent(self, event):
        row, column = self.pixels_to_logical(event.x(), event.y())

        if 0 <= row < self.array.shape[0] and 0 <= column < self.array.shape[1]:
            self.array[row, column] = self.selected

            self.update(*self.logical_to_pixels(row, column), self.CELL_SIZE, self.CELL_SIZE)

    def paintEvent(self, event):
        rect = event.rect()

        row_min, col_min = self.pixels_to_logical(rect.left(), rect.top())
        row_min = max(row_min, 0)
        col_min = max(col_min, 0)
        row_max, col_max = self.pixels_to_logical(rect.right(), rect.bottom())
        row_max = min(row_max + 1, self.array.shape[0])
        col_max = min(col_max + 1, self.array.shape[1])

        painter = QtGui.QPainter(self)

        for row in range(row_min, row_max):
            for column in range(col_min, col_max):
                x, y = self.logical_to_pixels(row, column)
                rect = QtCore.QRectF(x, y, self.CELL_SIZE, self.CELL_SIZE)
                SVG_WATER.render(painter, rect)

                if self.array[row, column] < 0:
                    SVG_SHARK.render(painter, rect)
                if self.array[row, column] > 0:
                    SVG_FISH.render(painter, rect)

    def wheelEvent(self, event):
        if event.modifiers() != QtCore.Qt.ControlModifier:
            return
        event.accept()
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()

    def logical_to_pixels(self, row, column):
        return column * self.CELL_SIZE, row * self.CELL_SIZE

    def pixels_to_logical(self, x, y):
        return y // self.CELL_SIZE, x // self.CELL_SIZE

    def update_size(self):
        size = self.logical_to_pixels(*self.array.shape)
        self.setMinimumSize(*size)
        self.setMaximumSize(*size)
        self.resize(*size)

    def zoom_in(self):
        if self.CELL_SIZE < 100:
            self.CELL_SIZE += max(int(self.CELL_SIZE * 0.1), 1)
            self.update_size()

    def zoom_out(self):
        if self.CELL_SIZE > 10:
            self.CELL_SIZE -= max(int(self.CELL_SIZE * 0.1), 1)
            self.update_size()


def new_dialog(window, grid):
    dialog = QtWidgets.QDialog(window)

    with open('wator/static/ui/newsimulation.ui') as f:
        uic.loadUi(f, dialog)

    result = dialog.exec()
    if result == QtWidgets.QDialog.Rejected:
        return

    width = dialog.findChild(QtWidgets.QSpinBox, 'widthBox').value()
    height = dialog.findChild(QtWidgets.QSpinBox, 'heightBox').value()
    nfish = dialog.findChild(QtWidgets.QSpinBox, 'nfishBox').value()
    nsharks = dialog.findChild(QtWidgets.QSpinBox, 'nsharksBox').value()

    if (nfish + nsharks) > width * height:
        QtWidgets.QMessageBox.critical(None, "Error", "Too many creatures for a specified simulation size!",
                                       QtWidgets.QMessageBox.Ok)
        return

    wator = WaTor(shape=(width, height), nfish=nfish, nsharks=nsharks)
    grid.array = wator.creatures
    grid.energy = wator.energies

    size = GridWidget.logical_to_pixels(grid, width, height)
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)
    grid.update()


def save(grid):
    file, _filter = QtWidgets.QFileDialog.getSaveFileName(None, 'Save Simulation')
    
    try:
        numpy.savetxt(file, grid.array)
    except:
        return


def load(grid):
    file, _filter = QtWidgets.QFileDialog.getOpenFileName(None, "Load Simulation")

    try:
        array = numpy.loadtxt(file, dtype=numpy.int8)
    except FileNotFoundError:
        return
    except:
        QtWidgets.QMessageBox.critical(None, "Error", "Invalid file!", QtWidgets.QMessageBox.Ok)
        return

    wator = WaTor(creatures=array)
    grid.array = wator.creatures
    grid.energy = wator.energies

    size = GridWidget.logical_to_pixels(grid.array.shape[0], grid.array.shape[1])
    grid.setMinimumSize(*size)
    grid.setMaximumSize(*size)
    grid.resize(*size)
    grid.update()


def tick(window, grid):
    wator = WaTor(creatures=grid.array, energies=grid.energy)

    age_fish = window.findChild(QtWidgets.QSpinBox, 'fishBox').value()
    age_shark = window.findChild(QtWidgets.QSpinBox, 'sharkBox').value()
    energy_eat = window.findChild(QtWidgets.QSpinBox, 'eat_energyBox').value()

    wator.set_age_fish(age_fish)
    wator.set_age_shark(age_shark)
    wator.set_energy_eat(energy_eat)
    wator.tick()

    grid.array = wator.creatures
    grid.energy = wator.energies
    grid.update()


def print_about():
    QtWidgets.QMessageBox.about(None, "About Wa-Tor SIMULATION",
                                "<b><center>Wa-Tor SIMULATION</center></b><br>Wa-Tor is a population dynamics"
                                " simulation devised by Alexander Keewatin Dewdney, implemented as a Python"
                                " module for the purpose of MI-PYT course at FIT CTU.<br><br><b>Implementation:"
                                "</b> Miroslav Hrončok, Marek Suchánek<br><b>GUI:</b> Igor Rosocha<br><b>GitHub:"
                                " </b><a href=\"https://github.com/IgorRosocha/Wa-Tor\">IgorRosocha/Wa-Tor</a><br>"
                                "<b>Lincensed</b> under </b><a href=\"https://github.com/IgorRosocha/Wa-Tor/blob/"
                                "master/LICENSE\"> GNU GPL v3</a><br><b>Special thanks</b> to <a href=\"opengameart"
                                ".org\">OpenGameArt.org</a> for providing the graphics content.")
    return


def main():
    app = QtWidgets.QApplication([])
    window = QtWidgets.QMainWindow()

    with open('wator/static/ui/mainwindow.ui') as f:
        uic.loadUi(f, window)

    wator = WaTor(shape=(15, 15), nfish=10, nsharks=10)

    scroll_area = window.findChild(QtWidgets.QScrollArea, 'scrollArea')
    grid = GridWidget(wator.creatures, wator.energies)
    scroll_area.setWidget(grid)
    palette = window.findChild(QtWidgets.QListWidget, 'palette')

    for creature, image, index in ('Water', WATER_PATH, 0), ('Fish', FISH_PATH, 1), ('Shark', SHARK_PATH, -1):
        item = QtWidgets.QListWidgetItem(creature)
        icon = QtGui.QIcon(image)
        item.setIcon(icon)
        item.setData(VALUE_ROLE, index)
        palette.addItem(item)

    def item_activated():
        for item in palette.selectedItems():
            grid.selected = item.data(VALUE_ROLE)

    palette.itemSelectionChanged.connect(item_activated)
    palette.setCurrentRow(0)

    action = window.findChild(QtWidgets.QAction, 'actionNew')
    action.triggered.connect(lambda: new_dialog(window, grid))

    action = window.findChild(QtWidgets.QPushButton, 'nextchrononButton')
    action.clicked.connect(lambda: tick(window, grid))

    action = window.findChild(QtWidgets.QAction, 'actionSave')
    action.triggered.connect(lambda: save(grid))

    action = window.findChild(QtWidgets.QAction, 'actionLoad')
    action.triggered.connect(lambda: load(grid))

    action = window.findChild(QtWidgets.QAction, 'actionQuit')
    action.triggered.connect(lambda: exit())

    action = window.findChild(QtWidgets.QAction, 'actionHelpAbout')
    action.triggered.connect(lambda: print_about())

    window.show()
    return app.exec()


if __name__ == "__main__":
    main()
