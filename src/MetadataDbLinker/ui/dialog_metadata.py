# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MetadataDialog
                                 A QGIS plugin
 MetadataDbLinker
                             -------------------
        begin                : 2016-04-04
        git sha              : $Format:%H$
        copyright            : (C) 2016 Septima P/S
        email                : kontakt@septima.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from __future__ import unicode_literals
import os
from distutils.util import strtobool
import uuid
from datetime import datetime
import json
import webbrowser  # for opening geodatainfo urls
from urllib.request import urlopen
from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QMessageBox,
    QListWidgetItem,
    QTableWidgetItem,
    QLineEdit,
    QTextEdit,
    QCheckBox,
    QLabel,
    QSizePolicy,
)
from qgis.PyQt.QtCore import QAbstractTableModel, Qt, pyqtSignal, QObject, pyqtSlot
from qgis.core import QgsBrowserModel, QgsLayerItem, QgsDataSourceUri
from qgis.gui import QgsBrowserTreeView, QgsActionMenu, QgsDateTimeEdit, QgsMessageBar

from ..core.taxonclassifier import TaxonClassifier
from ..core.qgislogger import QgisLogger
from ..config import *
from ..config import Settings
from ..core.metadatadblinkertool import MetadataDbLinkerTool

FORM_CLASS, _ = uic.loadUiType(
    os.path.join(os.path.dirname(__file__), "dialog_metadata.ui")
)


class MetaTableModel(QAbstractTableModel):
    """
    The model for the table view
    """

    def __init__(self, parent, mylist, header, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.mylist = mylist
        self.header = header

    def rowCount(self, parent):
        return len(self.mylist)

    def columnCount(self, parent):
        return len(self.mylist[0])

    def data(self, index, role):
        if not index.isValid():
            return None
        elif role != Qt.DisplayRole:
            return None
        return self.mylist[index.row()][index.column()]

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.header[col]
        return None

    def setData(self, d):
        self.mylist = d


class SelectedItemProxy(object):
    def __init__(self, table, uri):
        self.table = table
        self._uri = uri

    def layerName(self):
        return self.table

    def uri(self):
        return self._uri


class MetadataDialog(QDialog, FORM_CLASS):
    def __init__(
        self, parent=None, table=None, uri=None, schema=None, close_dialog=False
    ):
        """Constructor."""
        super(MetadataDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.field_def = []
        self.data_list = []
        # self.iface = iface

        if type(table) == tuple:
            table = table[1]

        self.schema = schema
        self.close_dialog = close_dialog
        self.settings = Settings()
        self.db_tool = MetadataDbLinkerTool()
        self.logger = QgisLogger("Metadata-DB-Linker")
        self.setupUi(self)
        self.bar = QgsMessageBar()
        self.bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.tab.layout().addWidget(self.bar, 0)

        self.model = QgsBrowserModel()
        self.model.initialize()  # Qgis 3.x specific
        self.tree = QgsBrowserTreeView()

        self.tree.setModel(self.model)

        self.treeDock.setWidget(self.tree)
        self.dateEdit.setDateTime(datetime.now())

        self.tree.selectionModel().selectionChanged.connect(self.selection_changed)

        self.saveRecordButton.clicked.connect(self.save_record)

        self.deleteRecordButton.clicked.connect(self.delete_record)

        self.geodatainfoEdit.textChanged.connect(self.lookup_geodatainfo_uuid)

        # ODENSE SPECIFIC
        # self.metadatabaseodkEdit.textChanged.connect(self.lookup_metadatabaseodk_uuid)

        #self.geodatainfoResult.setReadOnly(True)
        #self.geodatainfo_link.linkActivated.connect(webbrowser.open(self.geodatainfo_link))

        if self.scrollArea:
            self.scrollArea.setStyleSheet("QScrollArea {border: 0px}")

        self.kleNoLookupBtn.clicked.connect(self.lookup_kle_number)
        self.kleSuggestions.setReadOnly(True)

        self.selected_item = None
        self.guids = []
        self.currentlySelectedLine = None

        # GUI_TABLE: describes fields in GUI using a PG_table
        try:
            self.gui_table_exists = self.db_tool.validate_gui_table()
            self.field_def_properties = self.db_tool.get_field_def_properties()
            self.additional_field_properties = self.db_tool.get_additional_fields()
        except:
            self.gui_table_exists = False
            self.field_def_properties = None
            self.additional_field_properties = None

        self.add_qtfields_to_field_properties()

        if self.close_dialog:
            self.saveRecordButton.setText(self.tr("Save metadata and close"))

        if table:
            self.treeDock.setEnabled(False)
            self.selected_item = SelectedItemProxy(table, uri)
            self.update_grid()
            self.tableView.selectRow(0)
            self.activate_fields()

        # Add this back in when additional_fields work
        self.tabWidget.removeTab(1)

        # Hides the tableView (Is used as an internal structure can be shown for debug purposes)
        self.tableView.setVisible(True)

    def add_qtfields_to_field_properties(self):
        """ Saves a reference to the QT input field into the field_def_properties object
            Adds additional fields into the GUI at this point

            Used for validation rules. Set up validation signal
        """

        # connect the editable fields to validation check
        self.nameEdit.textEdited.connect(self.validate_metadata)
        self.descriptionEdit.textChanged.connect(self.validate_metadata)
        self.kleNoEdit.textEdited.connect(self.validate_metadata)
        self.responsibleEdit.textEdited.connect(self.validate_metadata)
        self.projectEdit.textChanged.connect(self.validate_metadata)
        self.geodatainfoEdit.textEdited.connect(self.validate_metadata)

        # self.metadatabaseodkEdit.textEdited.connect(self.validate_metadata)
        # self.metadatabaseodkEdit.hide()
        self.metadatabaseodkLabel.hide()
        self.metadatabaseodk_link.hide()
        # if the gui_table exists we can edit the labels with a "required" tag
        if self.gui_table_exists:

            f = self.field_def_properties
            # ODENSE SPECIFIC
            # Test if the column is in the field_def_properties, if yes, enable the field in the GUI
            rt = " (påkrævet)"
            try:
                odense_guid = f["metadata_odk_guid"]
                # odense_guid['qt_input'] = self.metadatabaseodkEdit
                # self.metadatabaseodkEdit.show()
                self.metadatabaseodkLabel.show()
                self.metadatabaseodk_link.show()

                if odense_guid["required"]:
                    self.metadatabaseodkLabel.setText(
                        self.metadatabaseodkLabel.text() + rt
                    )

            except:
                pass  # no odense column

            # TODO loop this from field_def_properties to tidy code
            # required text
            if f["name"]["required"]:
                self.nameLabel.setText(self.tr(self.nameLabel.text() + rt))
            if f["description"]["required"]:
                self.descriptionLabel.setText(
                    self.tr(self.descriptionLabel.text() + rt)
                )
            if f["kle_no"]["required"]:
                self.kleLabel.setText(self.tr(self.kleLabel.text() + rt))
            if f["responsible"]["required"]:
                self.responsibleLabel.setText(
                    self.tr(self.responsibleLabel.text() + rt)
                )
            if f["project"]["required"]:
                self.responsibleLabel.setText(
                    self.tr(self.responsibleLabel.text() + rt)
                )

            # custom labels (bit difficult to implement with current logic)
            # if f["name"]["label"]:
            #    self.nameLabel.setText(f["name"]["label"])
            # if f["description"]["label"]:
            #    self.descriptionLabel.setText(
            #        f["description"]["label"]
            #    )
            # if f["kle_no"]["label"]:
            #    self.kleLabel.setText(f["kle_no"]["label"])
            # if f["responsible"]["label"]:
            #    self.responsibleLabel.setText(
            #        f["responsible"]["label"]
            #    )
            # if f["project"]["label"]:
            #    self.responsibleLabel.setText(
            #        f["responsible"]["label"]
            #    )

            form_layout = self.additional_form
            # sort the additional_fields på id after request by Odense
            # Explain:
            # sorted(items) by k[1] (the value) on id
            # Then unpack the list of tuples and take the first element (which is the key)
            additional_fields = list(
                list(
                    zip(
                        *sorted(
                            self.additional_field_properties.items(),
                            key=lambda k: k[1]["id"],
                        )
                    )
                )[0]
            )
            for idx, x in enumerate(additional_fields):
                # For each additional_field add a row

                # If is_shown is false, we dont add it and continue
                field = self.additional_field_properties.get(x)
                is_shown = field.get("is_shown")

                if not is_shown:
                    continue

                displayname = field.get("displayname")
                if field.get("type") in ["text", "line", "multiline"]:

                    if field.get("type") in ["text", "line"]:
                        line_edit = QLineEdit()
                    elif field.get("type") == "multiline":
                        line_edit = QTextEdit()

                    line_edit.setEnabled(False)  # initialize as disabled

                    editable = field.get("editable")
                    required = field.get("required")

                    if required and editable:
                        displayname = self.tr(displayname) + self.tr(" (required)")

                    form_layout.addRow(QLabel(displayname), line_edit)

                    # Persist the line_edit so we can get it again later when validating the input
                    self.additional_field_properties.get(x)["qt_input"] = line_edit
                    # Add a signal to the line_edit to form_validate when the field is edited by the user
                    line_edit.textChanged.connect(self.validate_metadata)

                elif field["type"] == "date" or field["type"] == "datetime":
                    qgsdate = QgsDateTimeEdit()
                    qgsdate.clear()  # initialize with null date
                    qgsdate.setEnabled(False)  # initialize as disabled

                    self.additional_field_properties.get(x)["qt_input"] = qgsdate
                    form_layout.addRow(QLabel(displayname), qgsdate)

                elif field.get("type") in ["bool", "boolean"]:

                    bool_edit = QCheckBox()
                    editable = field.get("editable")
                    required = field.get("required")

                    if required and editable:
                        displayname = self.tr(displayname) + self.tr(" (required)")

                    form_layout.addRow(QLabel(displayname), bool_edit)

                    # Persist the line_edit so we can get it again later when validating the input
                    self.additional_field_properties.get(x)["qt_input"] = bool_edit
                    # Add a signal to the line_edit to form_validate when the field is edited by the user
                    # bool_edit.connect(self.validate_metadata)
                else:
                    QMessageBox.critical(
                        self,
                        self.tr("Could not validate additional field type for: %s" % x),
                        self.tr("See log for error details."),
                    )
        else:
            # If the table does not exist, remove the additional Fields tab
            self.tabWidget.removeTab(1)

        #f["name"]["qt_input"] = self.nameEdit
        #f["description"]["qt_input"] = self.descriptionEdit
        #f["kle_no"]["qt_input"] = self.kleNoEdit
        #f["responsible"]["qt_input"] = self.responsibleEdit
        #f["project"]["qt_input"] = self.projectEdit
        # f['geodatainfo_uuid']['qt_input'] = self.geodatainfoEdit

    def lookup_geodatainfo_uuid(self):
        """
        """
        geodatainfo_url = (
            "https://www.geodata-info.dk/srv/dan/catalog.search#/metadata/"
        )

        # get the UUID from the lineedit
        geodatainfo_uuid = self.geodatainfoEdit.text()

        # IF the paste is a LINK, strip the link part, and paste back the guid
        # TODO: regex this, if this is the functionality needed
        if("http" in self.geodatainfoEdit.text() and "metadata" in self.geodatainfoEdit.text()):
            self.geodatainfoEdit.setText(geodatainfo_uuid.split("/")[-1])
            geodatainfo_uuid = self.geodatainfoEdit.text()

        link_html = "<a href=%s>%s</a>" % (
            geodatainfo_url + geodatainfo_uuid,
            geodatainfo_url + geodatainfo_uuid,
        )
        self.geodatainfo_link.setText(link_html)
        self.geodatainfo_link.setOpenExternalLinks(True)

    def set_metadatabaseodk_uuid(self, guid):
        metadatabaseodk_url = "https://www.metadatabase.odknet.dk/theme/"
        metadatabaseodk_uuid = guid
        link_html = "<a href=%s>%s</a>" % (
            metadatabaseodk_url + metadatabaseodk_uuid,
            metadatabaseodk_url + metadatabaseodk_uuid,
        )
        self.metadatabaseodk_link.setText(link_html)
        self.metadatabaseodk_link.setOpenExternalLinks(True)

    def lookup_kle_number(self):
        taxon_url = self.settings.value("taxonUrl")
        taxon_taxonomy = self.settings.value("taxonTaxonomy")
        if not taxon_url or not taxon_taxonomy:
            self.logger.critical("No taxon url and/or taxonomy")
            QMessageBox.warning(
                self,
                self.tr("No taxon url and/or taxonomy"),
                self.tr(
                    "Please enter an url and taxonomy for Taxon service in settings."
                ),
            )
            return False

        taxon = TaxonClassifier(taxon_url, taxon_taxonomy)
        taxon_results = taxon.get(self.descriptionEdit.toPlainText())
        if taxon_results:
            presentation_str = ""
            kle_nrs = []
            for elem in taxon_results:
                tmp_presentation = "{} {}\n".format(elem["kle"], elem["title"])
                presentation_str += tmp_presentation
                kle_nrs.append(elem["kle"])
            # Set text in presentaion box
            self.kleSuggestions.setText(presentation_str)

            current_klr = self.kleNoEdit.text()
            str_klr_nrs = "{}".format(", ".join(kle_nrs))

            # set text in kle input box
            if current_klr != str_klr_nrs:
                if not current_klr == "":
                    self.kleNoEdit.setText(
                        "{}, {}".format(self.kleNoEdit.text(), ", ".join(kle_nrs))
                    )
                else:
                    self.kleNoEdit.setText("{}".format(", ".join(kle_nrs)))
        else:
            self.kleSuggestions.setText("No results from Taxon Classifier.")
            self.logger.info("No results from taxon service")

    def exec_(self):
        # TODO: improve this by having db_tool throw an exception and catch it out here with the message
        try:
            if self.db_tool.validate_structure():
                try:
                    if self.db_tool.validate_gui_table():
                        self.gui_table_exists = self.db_tool.validate_gui_table()
                        self.field_def_properties = (
                            self.db_tool.get_field_def_properties()
                        )
                        # self.additional_field_properties = (
                        #    self.db_tool.get_additional_fields()
                        # )
                except Exception as e:
                    self.logger.info(
                        "Could not validate gui_table setup, if you wish to use the gui_table please validate the settings"
                    )

                super(MetadataDialog, self).exec_()
        except Exception as e:
            QMessageBox.warning(self, self.tr("Please!"), self.tr(str(e)))
            # If there is an exception at this stage, close the dialog
            super(MetadataDialog, self).close()

    def get_selected_uri(self):
        """
        :return:
        """
        return self.selected_item.uri()

    def get_selected_db(self):
        return QgsDataSourceUri(self.selected_item.uri()).database()

    def get_selected_port(self):
        return QgsDataSourceUri(self.selected_item.uri()).port()

    def get_selected_host(self):
        return QgsDataSourceUri(self.selected_item.uri()).host()

    def get_selected_schema(self):
        """
        :return:
        """
        if self.schema is None or self.schema == "":
            return "public"
        else:
            return self.schema

    def get_selected_table(self):
        """
        :return:
        """
        return self.selected_item.layerName()

    def save_record(self):
        if self.currentlySelectedLine is None:
            self.add_record()
        else:
            self.update_record()

        if self.close_dialog:
            self.close()

    def table_row_selected(self, a, b):

        v = []
        idxs = a.indexes()
        for idx in idxs:
            r = idx.row()
            if r not in v:
                v.append(r)

        if len(v) > 0:

            guid = self.guids[v[0]]
            self.currentlySelectedLine = guid

            try:
                results = self.db_tool.select({"guid": guid})
            except RuntimeError:
                QMessageBox.critical(
                    self,
                    self.tr("Error selecting data."),
                    self.tr("See log for error details."),
                )

            if len(results) == 1:
                results = results[0]

                filtered_results = results.copy()
                # Filter out NULL results
                for res in filtered_results:
                    if str(results.get(res)) == "NULL" and results.get(res).isNull():
                        del results[res]

                self.schema = results.get("schema")

                if "name" in list(results):
                    self.nameEdit.setText(results.get("name"))

                if "description" in list(results):
                    self.descriptionEdit.setText(results.get("description"))

                if "ts_timezone" in list(results):
                    d = results.get("ts_timezone")
                    da = datetime.strptime(d, "%d/%m-%Y %H:%M")
                    self.dateEdit.setDate(da)

                if "kle_no" in list(results):
                    self.kleNoEdit.setText(results.get("kle_no"))

                if "responsible" in list(results):
                    self.responsibleEdit.setText(results.get("responsible"))

                if "project" in list(results):
                    self.projectEdit.setPlainText(results.get("project"))

                if 'geodatainfo_uuid' in list(results):
                    self.geodatainfoEdit.setText(results.get('geodatainfo_uuid') if str(results.get('geodatainfo_uuid')).lower() != "null" else "")

                #if 'metadata_odk_guid' in list(results):
                #    self.metadatabaseodkEdit.setText(results.get('metadata_odk_guid') if str(results.get('metadata_odk_guid')).lower() != "null" else "")

        else:
            self.currentlySelectedLine = None

    def delete_record(self):
        """
        Delete a record given its GUID.
        Empties the fields.
        """
        selected_rows = self.tableView.selectionModel().selectedRows()
        for row in selected_rows:
            guid = self.guids[row.row()]
            try:
                self.db_tool.delete({"guid": guid})
            except RuntimeError as e:
                # QMessageBox.critical(
                #    self,
                #    self.tr('Error deleting data.'),
                #    self.tr('See log for error details.')
                # )
                self.showMessage(self.tr(str(e)), level=1)

            self.update_grid()
            if self.has_table_data:
                self.tableView.selectRow(0)
        self.empty_fields()
        self.deleteRecordButton.setEnabled(False)

    def activate_fields(self):
        """
        Activates all fields and buttons.
        :return:
        """

        # use db_tool to check if gui_table exists
        if self.gui_table_exists:

            # The gui_table exists extract the editable information about fields.
            # If this is the first time, it will be a good idea to save configuration
            breakFlag = False
            try:
                f = self.field_def_properties
            except Exception as e:
                breakFlag = True

            if breakFlag is False:
                # Enable Fields based on whats written in gui_table
                self.nameEdit.setEnabled(f["name"]["editable"])
                self.descriptionEdit.setEnabled(f["description"]["editable"])
                self.kleNoEdit.setEnabled(f["kle_no"]["editable"])
                self.kleNoLookupBtn.setEnabled(f["name"]["editable"])
                self.responsibleEdit.setEnabled(f["responsible"]["editable"])
                self.projectEdit.setEnabled(f["project"]["editable"])
                self.geodatainfoEdit.setEnabled(f['geodatainfo_uuid']['editable'])
                self.dateEdit.setEnabled(True)

                # If the gui_table exists it means that validation rules should be enforced before button activates
                # self.saveRecordButton.setEnabled(True)
                self.deleteRecordButton.setEnabled(True)

                if self.gui_table_exists and self.additional_field_properties:
                    for field in self.additional_field_properties:
                        x = self.additional_field_properties.get(field)
                        if x.get("qt_input") and x.get("editable"):
                            x.get("qt_input").setEnabled(True)
                        else:
                            continue

        else:
            self.nameEdit.setEnabled(True)
            self.descriptionEdit.setEnabled(True)
            self.kleNoEdit.setEnabled(True)
            self.kleNoLookupBtn.setEnabled(True)
            self.responsibleEdit.setEnabled(True)
            self.projectEdit.setEnabled(True)
            self.dateEdit.setEnabled(True)
            self.geodatainfoEdit.setEnabled(True)

            self.saveRecordButton.setEnabled(True)
            self.deleteRecordButton.setEnabled(True)

    def deactivate_fields(self):
        """
        Deactivates all fields and buttons.
        :return:
        """
        self.nameEdit.setEnabled(False)
        self.descriptionEdit.setEnabled(False)
        self.kleNoEdit.setEnabled(False)
        self.kleNoLookupBtn.setEnabled(False)
        self.responsibleEdit.setEnabled(False)
        self.projectEdit.setEnabled(False)
        self.dateEdit.setEnabled(False)
        self.saveRecordButton.setEnabled(False)
        self.deleteRecordButton.setEnabled(False)

        if self.gui_table_exists and self.additional_field_properties:
            for field in self.additional_field_properties:
                x = self.additional_field_properties.get(field)
                if x.get("qt_input"):
                    x.get("qt_input").setEnabled(False)
                else:
                    continue

        self.geodatainfoEdit.setEnabled(False)

    @pyqtSlot("QItemSelection")
    def selection_changed(self, newSelection):
        """
        Triggered when the user clicks on a postgresql table in the tree.
        :param newSelection:
        :param oldSelection:
        :return:
        """
        self.empty_additional_fields()
        self.empty_fields()
        selected = newSelection.indexes()

        if len(selected) > 0:

            b = self.model.dataItem(selected[0])

            if type(b) == QgsLayerItem:

                self.schema = QgsDataSourceUri(b.uri()).schema()

                self.selected_item = b
                self.update_grid()
                self.activate_fields()

                if self.has_table_data:
                    self.tableView.selectRow(0)
                else:
                    self.tableView.setModel(None)
                    self.currentlySelectedLine = None
                    self.dateEdit.setDateTime(datetime.now())

                self.validate_metadata()
            else:
                self.deactivate_fields()

    def empty_fields(self):
        """
        Empties all fields.
        :return:
        """
        self.nameEdit.setText("")
        self.descriptionEdit.setText("")
        self.responsibleEdit.setText("")
        self.kleNoEdit.setText("")
        self.projectEdit.setPlainText("")
        self.kleSuggestions.setText("")
        self.geodatainfoEdit.setText('')
        self.geodatainfo_link.setText('')

        # ODENSE SPECIFIC
        #self.metadatabaseodkEdit.setText('')
        self.metadatabaseodk_link.setText("")
        if self.conn_info:
            self.conn_info.setText("")

    def empty_additional_fields(self):

        if self.gui_table_exists and self.additional_field_properties:
            for field in self.additional_field_properties:
                x = self.additional_field_properties.get(field)
                if x.get("qt_input"):
                    if type(x.get("qt_input")) == QLineEdit:
                        x.get("qt_input").clear()
                    elif type(x.get("qt_input")) == QCheckBox:
                        x.get("qt_input").setCheckState(False)
                    else:
                        x.get("qt_input").clear()
                else:
                    continue

    def update_grid(self):
        """
        Updates the grid.
        :return:
        """
        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()
        host = self.get_selected_host()
        results = []

        try:
            results = self.db_tool.select(
                {"host": host,"db": db, "port": port, "schema": schema, "sourcetable": table,},
                order_by={"field": "ts_timezone", "direction": "DESC"},
            )
        except RuntimeError as e:
            # QMessageBox.critical(
            #    self,
            #    self.tr('Error selecting data.'),
            #    self.tr('See log for error details.')
            # )
            self.showMessage(self.tr(str(e)), level=1)
        # Update conn_info if available
        if self.conn_info:
            c = 'Host: {host} DB: {db}:{port} "{schema}"."{table}"'.format(
                host=host, db=db, port=port, schema=schema, table=table
            )
            self.conn_info.setText(c)

        labels = [
            self.db_tool.get_field_def().get(f).get("label")
            for f in self.db_tool.field_order
            if "label" in self.db_tool.get_field_def().get(f)
        ]

        fields = self.db_tool.field_order

        # Populate extra fields
        if self.additional_field_properties:
            additional_fields = list(self.additional_field_properties.keys())
            form_layout = self.additional_form
        else:
            form_layout = self.additional_form
            additional_fields = []

        if len(results) > 0:
            rws = []
            self.guids = []

            for result in results:
                t = []
                for k in fields:
                    t.append(result.get(k))

                # If results, put data into additional fields
                for idx, x in enumerate(
                    additional_fields
                ):  # If there are no additional fields this enumerator is empty
                    d_type = self.additional_field_properties.get(x)["type"]
                    if d_type in ["text", "line", "multiline"]:
                        line_edit = self.additional_field_properties.get(x)["qt_input"]

                        if type(line_edit) == QTextEdit:
                            line_edit.setPlainText(
                                result.get(x)
                                if str(result.get(x)).lower() != "null"
                                else ""
                            )

                        else:
                            line_edit.setText(
                                result.get(x)
                                if str(result.get(x)).lower() != "null"
                                else ""
                            )

                    elif d_type in ["date", "datetime"]:
                        date_result = result.get(x)
                        date_edit = self.additional_field_properties.get(x)["qt_input"]

                        if str(date_result).lower() != "null":
                            if type(date_result) == str: #indicates that field in database was not timestamp, but character
                                date_edit.setDateTime(datetime.strptime(date_result,'%Y-%m-%d %H:%M:%S'))
                            else:
                                date_edit.setDateTime(date_result)

                    elif d_type in ["bool", "boolean"]:
                        bool_result = result.get(x)
                        bool_edit = self.additional_field_properties.get(x)["qt_input"]

                        try:
                            bool_edit.setChecked(strtobool(str(bool_result)))
                        except ValueError as e:  # Happens if str result is null
                            bool_edit.setChecked(False)

                rws.append(tuple(t))
                self.guids.append(result.get("guid"))

            table_model = MetaTableModel(self, rws, labels)

            if self.field_def_properties and "metadata_odk_guid" in self.field_def_properties.keys():
                self.set_metadatabaseodk_uuid(result["guid"])

            table_model.data(table_model.createIndex(0, 0), Qt.DisplayRole)

            self.tableView.setModel(table_model)
            self.tableView.selectionModel().selectionChanged.connect(
                self.table_row_selected
            )
            self.has_table_data = True
            # self.deleteRecordButton.setEnabled(True)

        else:
            self.has_table_data = False
            self.tableView.setModel(None)
            self.tableView.selectionModel().selectionChanged.disconnect()
            # self.deleteRecordButton.setEnabled(False)

    def show(self):
        super(MetadataDialog, self).show()

    def update_record(self):
        """
            Adds a record to the table.
            :return:
            """

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()
        host = self.get_selected_host()
        update_object = {
            "db": db,
            "port": port,
            "host": host,
            "schema": schema,
            "sourcetable": table,
            "guid": self.currentlySelectedLine,
            "name": self.nameEdit.text(),
            "description": self.descriptionEdit.toPlainText(),
            "ts_timezone": self.dateEdit.text(),
            "kle_no": self.kleNoEdit.text(),
            "responsible": self.responsibleEdit.text(),
            "project": self.projectEdit.toPlainText(),
        }
        _uuid = self.validate_uuid(self.geodatainfoEdit.text())
        if _uuid:
            update_object['geodatainfo_uuid'] = _uuid
        # If the gui_table exists add the additional_fields
        if self.gui_table_exists:
            form_layout = self.additional_form
            for idx, additional_field in enumerate(self.additional_field_properties):

                field = self.additional_field_properties.get(additional_field)
                if field["type"] in ["text", "line", "multiline"]:
                    if type(field["qt_input"]) == QTextEdit:
                        field_val = field["qt_input"].toPlainText()
                    else:
                        field_val = field["qt_input"].text()
                elif field["type"] == "date":
                    field_val = field["qt_input"].dateTime().toString("yyyy-MM-dd")
                elif field["type"] in ["datetime", "timestamp"]:
                    field_val = (
                        field["qt_input"].dateTime().toString("yyyy-MM-dd HH:mm:ss")
                    )
                elif field["type"] in ["bool", "boolean"]:
                    if field["qt_input"].isChecked():
                        field_val = "true"
                    else:
                        field_val = "false"
                else:
                    field_val = None

                update_object[additional_field] = {
                    "value": field_val,
                    "type": field["type"],
                }
        try:
            odense_guid = self.field_def_properties["metadata_odk_guid"]
            #update_object["metadata_odk_guid"] = self.validate_uuid(
            #    self.metadatabaseodkEdit.text()
            #)
        except:
            pass  # no field

        try:
            self.db_tool.update(update_object)
            QMessageBox.information(
                self,
                self.tr("Success!"),
                self.tr(
                    'Updated Name: "{}" successfully'.format(update_object["name"])
                ),
            )
        except RuntimeError as e:
            self.showMessage("Error updating data: " + self.tr(str(e)), level=1)

        self.update_grid()

    def add_record(self):
        """
        Adds a record to the table.
        :return:
        """

        guid = str(uuid.uuid4())

        db = self.get_selected_db()
        port = self.get_selected_port()
        schema = self.get_selected_schema()
        table = self.get_selected_table()
        host = self.get_selected_host()

        if table:
            try:
                insert_object = {
                    "guid": guid,
                    "db": db,
                    "port": port,
                    "schema": schema,
                    "host": host,
                    "sourcetable": table,
                    "name": self.nameEdit.text(),
                    "description": self.descriptionEdit.toPlainText(),
                    "ts_timezone": self.dateEdit.text(),
                    "kle_no": self.kleNoEdit.text(),
                    "responsible": self.responsibleEdit.text(),
                    "project": self.projectEdit.toPlainText(),
                }
                _uuid = self.validate_uuid(self.geodatainfoEdit.text())
                if _uuid:
                   insert_object['geodatainfo_uuid'] = _uuid
                try:
                    # odense_guid = self.field_def_properties['metadata_odk_guid']
                    odense_guid = guid
                    # sinsert_object['metadata_odk_guid'] = self.validate_uuid(self.metadatabaseodkEdit.text())
                except:
                    pass

                if self.gui_table_exists:
                    form_layout = self.additional_form
                    for idx, additional_field in enumerate(
                        self.additional_field_properties
                    ):

                        field = self.additional_field_properties.get(additional_field)
                        if field["type"] in ["text", "line", "multiline"]:
                            if type(field["qt_input"]) == QTextEdit:
                                field_val = field["qt_input"].toPlainText()
                            else:
                                field_val = field["qt_input"].text()
                        elif field["type"] == "date":
                            field_val = (
                                field["qt_input"].dateTime().toString("yyyy-MM-dd")
                            )
                        elif field["type"] in ["datetime", "timestamp"]:
                            field_val = (
                                field["qt_input"]
                                .dateTime()
                                .toString("yyyy-MM-dd HH:mm:ss")
                            )
                        elif field["type"] in ["bool", "boolean"]:
                            if field["qt_input"].isChecked():
                                field_val = True
                            else:
                                field_val = False
                        else:
                            field_val = None

                        insert_object[additional_field] = {
                            "value": field_val,
                            "type": field["type"],
                        }

                self.db_tool.insert(insert_object)
                self.currentlySelectedLine = guid
                self.update_grid()
                self.tableView.selectRow(0)

                QMessageBox.information(
                    self,
                    self.tr("Success!"),
                    self.tr(
                        'Inserted Name: "{}" successfully'.format(insert_object["name"])
                    ),
                )

            except Exception as e:
                print(e)
                QMessageBox.critical(
                    self,
                    self.tr("Error inserting data."),
                    self.tr("See log for error details."),
                )
        else:
            QMessageBox.information(
                self, self.tr("Please!"), self.tr("Remember to select a table.")
            )

    def validate_uuid(self, _uuid):
        """
            validates an uuid and returns it if valid
        """
        if len(_uuid) == 0:
            return False
        try:
            uuid_object = uuid.UUID(_uuid, version=4)
        except ValueError:
            self.logger.critical("UUID is not valid")
            QMessageBox.warning(
                self, self.tr("UUID is not valid"), self.tr("Please enter a valid UUID")
            )
            # raise RuntimeError("Geodata-info UUID is not valid")

        return _uuid

    def validate_metadata(self):
        """Validates the current metadata according to the field_properties. Activates the saveButton
        if everything is validated.


        """
        validated = True
        # Check if the gui_table exists
        if self.gui_table_exists:
            # If the table exists we can check the validation rules
            for field in self.field_def_properties:
                f = self.field_def_properties.get(field)
                try:
                    qt_input = f["qt_input"]
                    required = f["required"]
                    editable = f["editable"]
                    if required:
                        # Check the contents of the QTinput
                        if isinstance(qt_input, QLineEdit):
                            if len(qt_input.text()) < 1:
                                if (
                                    editable
                                ):  # If the user can't edit the field it can't break validation
                                    validated = False
                                break

                        elif isinstance(qt_input, QTextEdit):
                            if len(qt_input.toPlainText()) < 1:
                                if (
                                    editable
                                ):  # If the user can't edit the field it can't break validation
                                    validated = False
                                break

                except:  # if there is no input defined skip
                    pass

            # Check the additional fields
            for field in self.additional_field_properties:
                f = self.additional_field_properties.get(field)
                try:
                    qt_input = f["qt_input"]
                    required = f["required"]
                    editable = f["editable"]
                    if required:
                        # Check the contents of the QTinput
                        if isinstance(qt_input, QLineEdit):
                            if len(qt_input.text()) < 1:
                                if (
                                    editable
                                ):  # If the user can't edit the field it can't break validation
                                    validated = False
                                # Only one field has to break validation, break
                                break
                        else:
                            print("yes")
                        pass
                except:  # if there is no input defined skip
                    pass
        else:

            # If there is no gui_table there is no validation
            validated = True

        # If all fields are valid
        if validated:
            self.saveRecordButton.setToolTip(self.tr(""))
            self.saveRecordButton.setText(self.tr("Save metadata"))
            self.saveRecordButton.setEnabled(True)
        # If a field is not valid in the current configuration
        else:
            self.saveRecordButton.setToolTip(
                self.tr("All required fields need to be filled!")
            )
            self.saveRecordButton.setText(
                self.tr("Save metadata (required fields missing)")
            )
            self.saveRecordButton.setEnabled(False)

    def showMessage(self, message, level):
        # TODO: message level
        self.bar.pushMessage("Error: ", message, level=level)
