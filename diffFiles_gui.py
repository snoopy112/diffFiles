try:
    import os
    import sys
    import difflib
    import hashlib
    from PyQt5 import QtCore, QtWidgets
    from PyQt5.QtGui import QColor
except Exception as e:
    print('Error:', e)
    os.system("pause")
    sys.exit()


IGNORE_FILES_EXTS = 'jpg', 'jpeg', 'png', 'ttf', 'mo', 'so', 'bin', 'cgi', 'ico'
DELIMITER = '-' * 75

RED = 250, 20, 20
GREEN = 20, 120, 20
BLUE1 = 20, 20, 120
BLUE2 = 20, 20, 250
CYAN = 20, 160, 160
GRAY = 120, 120, 120


class Ui_Form(object):

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(700, 700)

        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")

        self.pathToFolder1 = QtWidgets.QLineEdit(Form)
        self.pathToFolder1.setObjectName("pathToFolder_1")
        self.pathToFolder1.setPlaceholderText('Path to folder 1')
        self.verticalLayout.addWidget(self.pathToFolder1)

        self.pathToFolder2 = QtWidgets.QLineEdit(Form)
        self.pathToFolder2.setObjectName("pathToFolder_2")
        self.pathToFolder2.setPlaceholderText('Path to folder 2')
        self.verticalLayout.addWidget(self.pathToFolder2)

        self.textBrowser = QtWidgets.QTextBrowser(Form)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        spacerItem = QtWidgets.QSpacerItem(0, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)

        self.pushButtonStart = QtWidgets.QPushButton(Form)
        self.pushButtonStart.setObjectName("pushButtonStart")
        self.horizontalLayout.addWidget(self.pushButtonStart)

        self.pushButtonClear = QtWidgets.QPushButton(Form)
        self.pushButtonClear.setObjectName("pushButtonClear")
        self.horizontalLayout.addWidget(self.pushButtonClear)

        self.horizontalLayout.addItem(spacerItem)

        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "diffFiles"))
        self.pushButtonStart.setText(_translate("Form", "Start"))
        self.pushButtonClear.setText(_translate("Form", "Clear"))


class BrowserHandler(QtCore.QObject):

    newTextAndColor = QtCore.pyqtSignal(str, object)

    def compare_files(self, path_to_file1, path_to_file2, mode="r", encoder=None):
        if encoder:
            file1 = open(path_to_file1, mode, encoding=encoder)
            file2 = open(path_to_file2, mode, encoding=encoder)
        else:
            file1 = open(path_to_file1, mode)
            file2 = open(path_to_file2, mode)

        if mode == "r":
            diff = difflib.unified_diff(
                file1.readlines(),
                file2.readlines(),
                fromfile=path_to_file1,
                tofile=path_to_file2)
        elif mode == "rb":
            hash1 = hashlib.md5()
            hash2 = hashlib.md5()
            hash1.update(file1.read())
            hash2.update(file2.read())

            diff = difflib.unified_diff(
                ['md5: {}'.format(hash1.hexdigest())],
                ['md5: {}'.format(hash2.hexdigest())],
                fromfile=path_to_file1,
                tofile=path_to_file2)
        else:
            self.newTextAndColor.emit('Wrong mode selected!', QColor(*RED))

        delimiter_flag = False
        for line in diff:
            delimiter_flag = True
            self.newTextAndColor.emit(line, QColor(*GREEN))

        if delimiter_flag:
            self.newTextAndColor.emit(DELIMITER, QColor(*GRAY))

        file1.close()
        file2.close()


    def bin_walk(self, path1, path2):
        while path1.endswith(('\\', '/', ' ')):
            path1 = path1[:-1]
        while path2.endswith(('\\', '/', ' ')):
            path2 = path2[:-1]

        for path in (path1, path2):
            if not os.path.exists(path) or not os.path.isdir(path):
                self.newTextAndColor.emit('Path doesn\'t exist: {}'.format(path), QColor(*RED))
                return

        for (dirpath_1, dirnames_1, filenames_1) in os.walk(path1):
            filenames_1 = set(filenames_1)
            dirnames_1 = set(dirnames_1)
            filenames_2 = set()
            dirnames_2 = set()

            dirpath_2 = os.path.join(path2, dirpath_1[len(path1)+1:])
            while dirpath_2.endswith(('\\', '/', ' ')):
                dirpath_2 = dirpath_2[:-1]

            if os.path.exists(dirpath_2):
                for entry in os.listdir(dirpath_2):
                    if os.path.isfile(os.path.join(dirpath_2, entry)):
                        filenames_2.add(entry)
                    elif os.path.isdir(os.path.join(dirpath_2, entry)):
                        dirnames_2.add(entry)
                    else:
                        pass

                diff_in_files = filenames_1 ^ filenames_2
                diff_in_folders = dirnames_1 ^ dirnames_2
                filenames = filenames_1 & filenames_2

                if len(diff_in_folders) != 0:
                    for i, path in enumerate((dirpath_1, dirpath_2)):
                        for folder in diff_in_folders:
                            if not os.path.isdir((os.path.join(path, folder))):
                                self.newTextAndColor.emit('Folder doesn\'t exist: {}'.format(os.path.join(path, folder)), QColor(*BLUE1))
                                for (missing_paths, _, missing_files) in os.walk(os.path.join(dirpath_2 if i == 0 else dirpath_1, folder)):
                                    for mis_file in missing_files:
                                        missing_path = os.path.join(dirpath_1 if i == 0 else dirpath_2, missing_paths[len(dirpath_2 if i == 0 else dirpath_1)+1:], mis_file)
                                        self.newTextAndColor.emit('File doesn\'t exist: {}'.format(missing_path), QColor(*BLUE2))
                                self.newTextAndColor.emit(DELIMITER, QColor(*GRAY))

                if len(diff_in_files) != 0:
                    for path in (dirpath_1, dirpath_2):
                        for file in diff_in_files:
                            if not os.path.isfile((os.path.join(path, file))):
                                self.newTextAndColor.emit('File doesn\'t exist: {}'.format(os.path.join(path, file)), QColor(*BLUE2))
                                self.newTextAndColor.emit(DELIMITER, QColor(*GRAY))

                for file in filenames:
                    if not file.lower().endswith(IGNORE_FILES_EXTS):
                        filename1 = os.path.join(dirpath_1, file)
                        filename2 = os.path.join(dirpath_2, file)

                        try:
                            self.compare_files(filename1, filename2, encoder="utf-8")
                        except UnicodeDecodeError as e:
                            try:
                                self.compare_files(filename1, filename2, encoder="utf16")
                            except UnicodeError as e:
                                try:
                                    self.compare_files(filename1, filename2, mode="rb")
                                except:
                                    self.newTextAndColor.emit('Can\'t open file: {}'.format(filename2), QColor(*GRAY))
                                    self.newTextAndColor.emit(DELIMITER, QColor(*GRAY))


    def run(self):

        self.newTextAndColor.emit('---Start---', QColor(*CYAN))

        path1 = window.ui.pathToFolder1.displayText()
        path2 = window.ui.pathToFolder2.displayText()

        self.bin_walk(path1, path2)

        self.newTextAndColor.emit('----End----', QColor(*CYAN))


class MyWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.thread = QtCore.QThread()

        self.browserHandler = BrowserHandler()
        self.browserHandler.moveToThread(self.thread)
        self.browserHandler.newTextAndColor.connect(self.addNewTextAndColor)

        self.ui.pushButtonStart.clicked.connect(self.browserHandler.run)
        self.ui.pushButtonClear.clicked.connect(self.clearBrowser)

        self.thread.start()

    @QtCore.pyqtSlot(str, object)
    def addNewTextAndColor(self, string, color):
        self.ui.textBrowser.setTextColor(color)
        self.ui.textBrowser.append(string)

    @QtCore.pyqtSlot()
    def clearBrowser(self):
        self.ui.textBrowser.clear()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec())
