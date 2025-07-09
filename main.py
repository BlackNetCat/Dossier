from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QLabel, QWidget,QGridLayout, \
    QLineEdit, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
    QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class DatabaseConnection:
    def __init__(self, database_file="database.db"):
        self.database_file = database_file

    def connect(self):
        connection = sqlite3.connect(self.database_file)
        return connection

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dossier")
        self.setMinimumSize(800,600)

        file_menu_item = self.menuBar().addMenu("&File")
        edit_menu_item = self.menuBar().addMenu("&Edit")
        help_menu_item = self.menuBar().addMenu("&Help")

        add_person_action = QAction(QIcon("icons/add.png"),"Add Person", self)
        add_person_action.triggered.connect(self.insert)
        file_menu_item.addAction(add_person_action)

        search_action = QAction(QIcon("icons/search.png"),"Search", self)
        search_action.triggered.connect(self.search)
        edit_menu_item.addAction(search_action)

        about_action = QAction("About", self)
        help_menu_item.addAction(about_action)
        about_action.triggered.connect(self.about)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(("Id", "Name", "Rank", "Mobile"))
        self.table.verticalHeader().setVisible(False)
        self.setCentralWidget(self.table)

        # Create toolbar
        toolbar = QToolBar()
        toolbar.setMovable(True)
        self.addToolBar(toolbar)
        toolbar.addAction(add_person_action)
        toolbar.addAction(search_action)

        # Create status bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)

        # Detect a cell click
        self.table.cellClicked.connect(self.cell_clicked)

    def cell_clicked(self):
        edit_button = QPushButton("Edit Record")
        edit_button.clicked.connect(self.edit)

        delete_button = QPushButton("Delete Record")
        delete_button.clicked.connect(self.delete)

        children = self.findChildren(QPushButton)
        if children:
            for child in children:
                self.statusbar.removeWidget(child)

        self.statusbar.addWidget((edit_button))
        self.statusbar.addWidget((delete_button))

    def load_data(self):
        connection = DatabaseConnection().connect()
        result = connection.execute("SELECT * FROM persons")
        self.table.setRowCount(0)
        for row_number, row_data in enumerate(result):
            self.table.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
        connection.close()

    def insert(self):
        dialog = InsertDialog()
        dialog.exec()

    def search(self):
        dialog = SearchDialog()
        dialog.exec()

    def edit(self):
        dialog = EditDialog()
        dialog.exec()

    def delete(self):
        dialog = DeleteDialog()
        dialog.exec()

    def about(self):
        dialog = AboutDialog()
        dialog.exec()

class EditDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Update Person Data")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Get person name from selected row
        index = dossier.table.currentRow()
        person_name = dossier.table.item(index, 1).text()

        # Get id from selected row
        self.person_id = dossier.table.item(index, 0).text()

        # Update person name widget
        self.person_name = QLineEdit(person_name)
        self.person_name.setPlaceholderText("Name")
        layout.addWidget(self.person_name)

        # Add combo box of ranks
        rank_name = dossier.table.item(index, 2).text()
        self.rank_name = QComboBox()
        ranks = ["Soldier", "Senior Soldier", "Junior Sergeant", "Sergeant", "Senior Sergeant"]
        self.rank_name.addItems(ranks)
        self.rank_name.setCurrentText(rank_name)
        layout.addWidget(self.rank_name)

        # Add mobile widget
        mobile = dossier.table.item(index, 3).text()
        self.mobile = QLineEdit(mobile)
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Update")
        button.clicked.connect(self.update_person)
        layout.addWidget(button)

        self.setLayout(layout)

    def update_person(self):
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("UPDATE persons SET name = ?, rank = ?, mobile = ? WHERE id = ?",
                       (self.person_name.text(),
                        self.rank_name.itemText(self.rank_name.currentIndex()),
                        self.mobile.text(),
                        self.person_id))
        connection.commit()
        cursor.close()
        connection.close()

        # Refresh the table
        dossier.load_data()

class DeleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Delete Person Data")

        layout = QGridLayout()
        confirmation = QLabel("Are you sure you want to delete?")
        yes = QPushButton("Yes")
        no = QPushButton("No")

        layout.addWidget(confirmation, 0, 0, 1, 2)
        layout.addWidget(yes, 1, 0)
        layout.addWidget(no, 1, 1)
        self.setLayout(layout)

        yes.clicked.connect(self.delete_person)

    def delete_person(self):
        # Get selected row index and  person id
        index = dossier.table.currentRow()
        person_id = dossier.table.item(index, 0).text()

        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("DELETE from persons WHERE id = ?", (person_id,))
        connection.commit()
        cursor.close()
        connection.close()
        dossier.load_data()

        self.close()

        confirmation_widget = QMessageBox()
        confirmation_widget.setWindowTitle("Success")
        confirmation_widget.setText("The record was deleted successfuly!")
        confirmation_widget.exec()

class InsertDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add new person")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add person name widget
        self.person_name = QLineEdit()
        self.person_name.setPlaceholderText("Name")
        layout.addWidget(self.person_name)

        # Add combo box of ranks
        self.rank_name = QComboBox()
        ranks = ["Soldier", "Senior Soldier", "Junior Sergeant", "Sergeant", "Senior Sergeant"]
        self.rank_name.addItems(ranks)
        layout.addWidget(self.rank_name)

        # Add mobile widget
        self.mobile = QLineEdit()
        self.mobile.setPlaceholderText("Mobile")
        layout.addWidget(self.mobile)

        # Add a submit button
        button = QPushButton("Register")
        button.clicked.connect(self.add_person)
        layout.addWidget(button)

        self.setLayout(layout)
    def add_person(self):
        name = self.person_name.text()
        rank = self.rank_name.itemText(self.rank_name.currentIndex())
        mobile = self.mobile.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO persons (name, rank, mobile) VALUES (?, ?, ?)",
                       (name, rank, mobile))
        connection.commit()
        cursor.close()
        connection.close()
        dossier.load_data()
class SearchDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Search person")
        self.setFixedWidth(300)
        self.setFixedHeight(300)

        layout = QVBoxLayout()

        # Add search name
        self.person_name = QLineEdit()
        self.person_name.setPlaceholderText("Name")
        layout.addWidget(self.person_name)

        # Create button
        button = QPushButton("Search")
        button.clicked.connect(self.search)
        layout.addWidget(button)

        self.setLayout(layout)

    def search(self):
        name = self.person_name.text()
        connection = DatabaseConnection().connect()
        cursor = connection.cursor()
        result = cursor.execute("SELECT * FROM persons WHERE name = ?",(name,))
        rows = list(result)
        items = dossier.table.findItems(name, Qt.MatchFlag.MatchFixedString)
        for item in items:
            print(item)
            dossier.table.item(item.row(),1).setSelected(True)

        cursor.close()
        connection.close()

class AboutDialog(QMessageBox):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        content = """
        Dossier CRUD system by PyQt6
        """
        self.setText(content)


app = QApplication(sys.argv)
dossier = MainWindow()
dossier.show()
dossier.load_data()
sys.exit(app.exec())