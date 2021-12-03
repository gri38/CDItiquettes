# -*-coding:utf-8 -*

from logging import shutdown
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5 import QtWebEngineWidgets
from PyQt5 import uic
from pathlib import Path
import math
import shutil
import os
from Codebar import Codebar
import base64
import webbrowser
from functools import partial
import uuid

from utils import get_version

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui = uic.loadUi(Path(__file__).parent / "MainWindow.ui", self)
        self.version_on_title()
        self.set_validators()
        self.update_preview("")

    def init_work(self):
        shutil.rmtree(self.get_work_folder(), ignore_errors=True)
        self.get_work_folder().mkdir(parents=True, exist_ok=True)

    def get_work_folder(self):
        return Path(os.path.expandvars("%APPDATA%")) / Path('CDItiquettes/work')

    def version_on_title(self):
        """ Gets the version in file version and append to the window title
        """
        version = get_version()
        title = self.windowTitle()
        title = f"{title} (version {version})"
        self.setWindowTitle(title)

    def set_validators(self):
        self.R_lineEdit.setValidator(QIntValidator(1, 1000, self))
        self.C_lineEdit.setValidator(QIntValidator(1, 1000, self))
        self.d1_lineEdit.setValidator(QDoubleValidator(0.1, 15.0, 2, self))
        self.d2_lineEdit.setValidator(QDoubleValidator(0.1, 11.0, 2, self))
        self.d3_lineEdit.setValidator(QDoubleValidator(0.1, 15.0, 2, self))
        self.d4_lineEdit.setValidator(QDoubleValidator(0.1, 11.0, 2, self))
        self.l_lineEdit.setValidator(QDoubleValidator(0.1, 21.0, 2, self))
        self.h_lineEdit.setValidator(QDoubleValidator(0.1, 297.0, 2, self))
        self.start_lineEdit.setValidator(QIntValidator(1, 1000000, self))

    def on_create(self):
        # if not self.L_lineEdit.text() or \
        # not self.C_lineEdit.text() or \
        # not self.d1_lineEdit.text() or \
        # not self.d2_lineEdit.text() or \
        # not self.d3_lineEdit.text() or \
        # not self.d4_lineEdit.text() or \
        # not self.d5_lineEdit.text() or \
        # not self.d6_lineEdit.text() or \
        # not self.start_lineEdit.text():
        #     QMessageBox.information(self, "Config incomplète", "Merci de remplir tous les champs de la configuration de la feuille.")
        #     return

        self.create_pushButton.setEnabled(False)

        self.init_work()

        with open("page.html", "r") as template_html:
            html = template_html.read()
            html = html.replace("d1_placeholder_", self.d1_lineEdit.text())
            html = html.replace("d2_placeholder_", self.d2_lineEdit.text())
            html = html.replace("d3_placeholder_", self.d3_lineEdit.text())
            html = html.replace("d4_placeholder_", self.d4_lineEdit.text())
            html = html.replace("l_placeholder_", self.l_lineEdit.text())
            html = html.replace("h_placeholder_", self.h_lineEdit.text())
            html = html.replace("text_size_placeholder_", str(self.text_size_spinBox.value()))
            html = html.replace("number_size_placeholder_", str(self.number_size_spinBox.value()))
            text_bold = self.text_bold_checkBox.isChecked()
            number_bold = self.number_bold_checkBox.isChecked()
            text_weight = "font-weight: normal"
            if text_bold:
                text_weight = "font-weight: bold"
            number_weight = "font-weight: normal"
            if number_bold:
                number_weight = "font-weight: bold"
            html = html.replace("text_weight_placeholder", text_weight)
            html = html.replace("number_weight_placeholder", number_weight)

            stickers_html = ""
            row_count = int(self.R_lineEdit.text())
            col_count = int(self.C_lineEdit.text())
            number_start = int(self.start_lineEdit.text())
            for row in range(row_count):
                for col in range(col_count):
                    cell_html = ""
                    if col == 0:
                        cell_html = cell_html + """<div class="left"></div>"""
                    if col > 0:
                        cell_html = cell_html + """<div class="hz_spacer"></div>"""
                    number = number_start + col + row * col_count
                    cb = Codebar(self.get_work_folder())
                    barcode_file = cb.save(str(number))
                    encoded_string = ""
                    with open(barcode_file, "rb") as image_file:
                        encoded_string = base64.b64encode(image_file.read())
                    cell_html = cell_html + f"""<div class="cell">
                    <div class="text">{self.sticker_text_lineEdit.text()}</div>
                    <div class="barcode"><img src="data:image/png;base64,{encoded_string.decode('ascii')}"></div>
                    <div class="number">{number}</div>
                    </div>"""

                    
                    stickers_html = stickers_html + cell_html
                    if row < row_count - 1:
                        if col == col_count - 1:
                            stickers_html = stickers_html + """<div style="clear:both"></div>"""
                            stickers_html = stickers_html + """<div class="vt_spacer"></div>"""

            html = html.replace("stickers_placeholder", stickers_html)

            html_file = self.get_work_folder() / (str(uuid.uuid4()) + ".html")
            pdf_file = self.get_work_folder() / (str(uuid.uuid4()) + ".pdf")
            with open(html_file, "w") as output:
                output.write(html)

            loader = QtWebEngineWidgets.QWebEngineView()
            loader.setZoomFactor(1)
            loader.setHtml(html)
            loader.loadFinished.connect(partial(self.produce_pdf, loader, str(pdf_file)))
            loader.page().pdfPrintingFinished.connect(self.open_pdf)

    def produce_pdf(self, loader, pdf_file):
        loader.page().printToPdf(pdf_file)

    def open_pdf(self, pdf_file, success):
        self.create_pushButton.setEnabled(True)
        if not success:
            QMessageBox.critical(self, "Erreur", "La génération du pdf a échoué.")
            return
        webbrowser.open(pdf_file)


    def get_preview_cell(self, text, number, width, height, text_size, number_size, text_bold,
                         number_bold):
        text_weight = "font-weight: normal"
        if text_bold:
            text_weight = "font-weight: bold"
        number_weight = "font-weight: normal"
        if number_bold:
            number_weight = "font-weight: bold"
        cell_html = f"""<!DOCTYPE html>
<html lang="en">
<meta charset="UTF-8">
<style>
    html,body {{
    height: 100%;
    width: 100%;
    margin: 0;
    padding: 0;
    background-color: #F0F0F0;
    }}
    body {{
        position: relative;
    }}
    .cell {{
        background-color: #FFF;
        height: {height}mm;
        width: {width}mm;
        border: 1px solid black;
        display: flex;
        flex-direction: column;
        position: absolute;
        left: 50%;
        top: 50%;
        margin-left: -{int(math.floor(float(width))/2)}mm;
        margin-top: -{int(math.floor(float(height))/2)}mm;
    }}
    .text {{
        text-align: center;
        flex-grow: 1;
        height: 33.33333%;
        display: flex;
        justify-content: center;
        align-content: center;
        flex-direction: column;
        font-size: {text_size}px;
        {text_weight};
    }}
    .number {{
        font-size: {number_size}px;
        height: 33.33333%;
        text-align: center;
        flex-grow: 1;
        display: flex;
        justify-content: center;
        align-content: center;
        flex-direction: column;
        {number_weight};
    }}
    .barcode {{
        height: 33.33333%;
        flex-grow: 1;
    }}
    #over {{
        width:100%;
        height:100%
    }}
    .barcode img {{
        width: 95%;
        height: 100%;
        margin-left: auto;
        margin-right: auto;
        display: block;
    }}
</style>
<body>
    <div class="cell">
        <div class="text">{text}</div>
        <div class="barcode">
            <div id="over">
                <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAZcAAABnCAYAAADMgw+gAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAYOSURBVHhe7ddna1TtFgbgnURNbDGxkMR/K4KKiAUVFURQQbEiCBZEVFCwoGJBRFQEyxd7777nXQ/Zw5g8OcbDOt+uCxYJ96w9M2ZmPzf2/POvBgAS9Y7/BIA0ygWAdMoFgHTKBYB0ygWAdMoFgHSTyqWnp6fMsmXLxpPJnjx50oyOjpa95cuXl+zx48fNyMhI5/qJs2LFirL36NGjZvHixdWdmFWrVpW9Bw8eNMPDwyVbvXp1ye7fv98MDQ1NuqadNWvWlL179+41g4ODJVu7dm3J7t6928ybN69k69atK1nNnTt3mjlz5pS9DRs2lOz27dvNwMBA53UmzqZNm8rezZs3m1mzZpVs8+bNJau5fv1609fXV/a2bt1asmvXrjW9vb0l27ZtW8lqrly50nnd7du3j6eTXbp0qbO3Y8eOkl28eLGT1Wbnzp1l78KFC51s165dJTt//nwn2717d8lqzp0719nbs2dPyc6ePdvJarNv376yd/r06U62f//+ktWcOnWqs3fo0KGSnTx5spMdPny4ZCdOnOhktTly5EjZO3bsWPXxdo4ePVr24mft8XbieUI8b5sdP368ZDXxPtu9eP/h4MGDnSz+neHAgQOdrDbxdwvxd2yzM2fOlGzv3r2/7U6c+LymEp9zuxeff4jvQ5vF9yTE96bNahPfuxDfw9rj7Vy+fLnsxfe69ng7V69eLXs1cT/FTtxfcZ+FLVu2lGzmzJnNjRs3Shb3Z2Rxv8Z9G+I+jqy/v7+5detWyTZu3FiyuP/jHJjK+vXry15t4tyJ8yfEeRRZnE9xToU4tyZe006cd3HuhTgHI4tz8eHDhyWrWblyZdmLczbO2xDnb/fzdk+c23F+hzjPazsxY2NjzdOnT8te9EObT8X/XABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEinXABIp1wASKdcAEg3qVyWLl1aZv78+ePJZH19fc3IyMhve5GNjo52rp84f7s3Y8aMzt68efMmZbXp3hsbG/tjVlPbmzlzZierzdy5cyfttVlN7NWunZjVzJo166/35syZMymrTW3vv2U1/f39nb3Zs2dPympT22uzmj+9RpsNDAx0strE4//vvTariffZ7sX7n05Wm4xra+Jzbvfi859OVpu/3Yvvde3xduJemUr3te1em8W9mZHVxFkRe7WJa+Nc6d6rZbWJ827iXndWE2douxfnbXdWm+nuxZlf25tKzz//Gv+9ePbsWfkZF8fU/Pz5s3n+/Hnz69evzl53VjM4OFj+ONPd+/HjR/PixYuyV8tquvfiNeKfVssWLFhQvjQ1tb3urKbd+/79e3l/f3qN2IvnC93XttnQ0NCUB/h09759+1beS2j3urOa2l4tGx4eLodWTW3vT6/b7n39+rV5+fLlb1lN997ChQvLAf6nrOZv9758+dK8evVqPJ1s0aJF5bDu3muzmtpeLfv8+XPz+vXrktXU9qZ77eLFizuH+kTd17Z7nz59at68eTNlVjPdvSVLlpQDfLp7NR8/fmzevn1bfm/32qynp6e8l/81i+eb6lDvft2Juq/98OFD8+7du2pW09vbW95L915kcW170E9U2/vTa7R779+/L1MTj8d7mbhXL5im+Q9PNWWij9kewwAAAABJRU5ErkJggg==">
            </div>
        </div>
        <div class="number">{number}</div>
    </div>
</body>
</html>"""
        with open("debug.html", "w") as debug:
            debug.write(cell_html)
        return cell_html

    def update_preview_2(self):
        self.update_preview("")

    def update_preview(self, _):
        text = self.sticker_text_lineEdit.text()
        number = self.start_lineEdit.text()
        width = self.l_lineEdit.text()
        height = self.h_lineEdit.text()
        text_size = self.text_size_spinBox.value()
        number_size = self.number_size_spinBox.value()
        text_bold = self.text_bold_checkBox.isChecked()
        number_bold = self.number_bold_checkBox.isChecked()
        self.preview_widget.setHtml(self.get_preview_cell(text,
                                                          number,
                                                          width,
                                                          height,
                                                          text_size,
                                                          number_size,
                                                          text_bold,
                                                          number_bold))
        
        


