import sys
import os 
import codecs
import CrowSyntax
import popplerqt4
import re
from PyQt4 import QtGui, QtCore

class Editor(QtGui.QMainWindow):
    
    def __init__(self):
        super(Editor, self).__init__()
        self.setGeometry(50,50,500,300)
        self.setWindowTitle("CrowTex")
        self.setWindowIcon(QtGui.QIcon('Crow.png'))
        
        self.pdf_view = QtGui.QDockWidget("PDF", self)
        
        self.newAction = QtGui.QAction("&New file",self)
        self.newAction.setShortcut("Ctrl+N")
        self.newAction.setStatusTip('Open new file')
        self.newAction.triggered.connect(self.file_new)
        self.openAction = QtGui.QAction("&Open file",self)
        self.openAction.setShortcut("Ctrl+O")
        self.openAction.setStatusTip('Open existing file')
        self.openAction.triggered.connect(self.file_open)
        self.saveAction = QtGui.QAction("&Save file",self)
        self.saveAction.setShortcut("Ctrl+S")
        self.saveAction.setStatusTip('Save file')
        self.saveAction.triggered.connect(self.file_save)
        self.saveAction.setEnabled(False) 
        self.saveAsAction = QtGui.QAction("&Save file as",self)
        self.saveAsAction.setShortcut("Ctrl+Shift+S")
        self.saveAsAction.setStatusTip('Save file with different name')
        self.saveAsAction.triggered.connect(self.file_save_as) 
        self.saveAsAction.setEnabled(False)
        self.compileAction = QtGui.QAction("&Compile file",self)
        self.compileAction.setShortcut("Ctrl+R")
        self.compileAction.setStatusTip('Compile file')
        self.compileAction.triggered.connect(self.file_compile)
        self.compileAction.setEnabled(False) 
        self.pdf_out = False
        
        self.statusBar()
        mainMenu = self.menuBar()
        fileMenu = mainMenu.addMenu('&File')
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.saveAsAction)
        fileMenu.addAction(self.compileAction)
        
        self.show()
    
    def file_new(self):
        self.saveAction.setEnabled(True)
        self.saveAsAction.setEnabled(True)
        self.compileAction.setEnabled(True)
        self.fileName = ' '    
        self.text_widget()
        self.setUnsaved(True)
        
    def file_open(self):

        self.fileName = QtGui.QFileDialog.getOpenFileName(self,'Open File')
        _file = codecs.open(self.fileName, 'r', 'utf-8')
        
        self.text_widget()
            
        with _file:
            text = _file.read()
            self.textEdit.setText(text)
            self.saveAction.setEnabled(True)
            self.saveAsAction.setEnabled(True)
            self.compileAction.setEnabled(True)
            self.setUnsaved(False)
            
    def file_save(self):
        if self.fileName == ' ':
            self.file_save_as()
        else:
            name = self.fileName
            _file = codecs.open(self.fileName, 'w', 'utf-8')
            text = self.textEdit.toPlainText()
            _file.write(text)
            _file.close()
        self.setUnsaved(False)
        
    def file_save_as(self):
        self.fileName = QtGui.QFileDialog.getSaveFileName(self, 'Save File')
        _file = codecs.open(self.fileName, 'w', 'utf-8')
        text = self.textEdit.toPlainText()
        _file.write(text)
        _file.close()
        self.setUnsaved(False)
    
    def file_compile(self):
        if self.fileName == ' ':
            self.file_save_as()
        
        os.system("pdflatex "+ self.fileName)
        self.show_pdf()
    
    def show_pdf(self):
        pdf_name = str(re.sub('\.tex$','.pdf',self.fileName))
        self.pdf_doc = popplerqt4.Poppler.Document.load(pdf_name)
        self.page = self.pdf_doc.page(0)
        self.image = self.page.renderToImage(300,300)
        self.pixmap = QtGui.QPixmap.fromImage(self.image)
        self.label = QtGui.QLabel(self)
        self.label.setPixmap(self.pixmap)
        self.pdf_view.setWidget(self.label)
        
        if not self.pdf_out:
            self.pdf_view.setFloating(False)
            self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.pdf_view)
        else:
            self.pdf_out = True
    
    def text_widget(self):
        self.textEdit = QtGui.QTextEdit()
        self.highlight = CrowSyntax.LatexHighlighter(self.textEdit.document())
        self.setCentralWidget(self.textEdit)
        self.textEdit.textChanged.connect(lambda: self.setUnsaved(True))
    
    def setUnsaved(self, state):
        self.unsaved = state
        if state:
            self.textEdit.textChanged.disconnect()
        else:
            self.textEdit.textChanged.connect(lambda: self.setUnsaved(True))
    
    def closeEvent(self,event):
        if self.unsaved:
            choice = QtGui.QMessageBox.question(self,'Fly away',
                                                "Migrate?",
                                                QtGui.QMessageBox.Yes|QtGui.QMessageBox.No)
            if choice == QtGui.QMessageBox.Yes:
                event.accept()
            else:
                event.ignore()           
        else:
            event.accept()
            
if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    GUI = Editor()
    sys.exit(app.exec_())
    
