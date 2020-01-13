# qgis-metadatafunctionality
The purpose of this QGIS plugin is to make it possible to enter metadatainformation (name, description, kle-journalnumber, date-of-creation-table) for a table in database through DB Manager.

# Installation and setup
The MetadataDBLinker plugin requires as minimum one table where metadata is stored, and an optional table describing the fields in the graphical user interface. The plugin can be installed using the install plugin from zip option in QGIS. ZIP files can be found and downloaded under `releases` for this Github Repository. 

![options](figures/installzip.PNG?raw=true "Installing the Plugin")

## First time setup
First time setting up the plugin the metadata table should be created and settings filled out accordingly. Navigate to the settings window in QGIS `Settings -> Options` and MetadataDBLinker will have its own tab. 


![settings](figures/options.PNG?raw=true "MetadataDbLinker Options")

MetadataDBLinker allows a dedicated user to be used with the metadata table. Access rights to this user can be controlled in PostgreSQL. Click the `Metadata Table (SQL)` button for an SQL CREATE statement that will create the table. Create the table in your PostgreSQL Database, make sure your user has approriate access to it then fill out the settings. Finally test the connection by clicking the test button, if OK the plugin should be working.

![options](figures/settings.PNG?raw=true "Settings")

### Gui Table

An extra table can optionally be configured to describe if certain GUI fields in the dialog should be required or enabled. The `Save metadata` button will be greyed out if required fields are not filled. Click the `Gui Table (SQL)` button in the settings for an SQL CREATE statement to set up this table.

Rows in this table refers columns in the `metadata` table by the `metadata_col_name` column. The table contains three boolean columns: `required`, `editable` and `is_shown` which can be set for every entry in the `metadata` table. 

## Usage

The plugin can be accessed in two ways. If the plugin is configured and active it can be reached from the toolbar. The plugin will also automatically start after importing layers into DB-manager. Click a layer in the browser within plugin to assign metadata, or if the dialog was started from DB-manager the layer is already selected. Fill out the metadata accordingly and hit `Save metadata` when done. The metadata fields will be enabled when a layer is selected in the browser. If a layer already has metadata assigned these fields will be filled and can be updated. 


![dblinker](figures/dblinker.PNG?raw=true "Metadata-DB-linker")

## Locator

As an added feature, layers with added metadata can be searched using the QGIS Locator by their metadata fields under the category "Metadata-DB-Linker". Clicking the entries will add to them to the current active project. 

![dblinker](figures/locator.PNG?raw=true "Metadata-DB-linker")
