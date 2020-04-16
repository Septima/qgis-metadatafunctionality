-- Default felterne
INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('guid','text','false','true','false','Guid','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('name','text','false','true','true','Name','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('description','text','false','true','true','Description','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('kle_no','text','false','true','true','Kle No','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('responsible','text','false','true','true','Responsible','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('project','text','false','true','true','Project','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('host','text','false','true','false','Host','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('db','text','false','true','false','Db','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('port','text','false','true','false','Port','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('schema','text','false','true','false','Schema','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('sourcetable','text','false','true','false','Sourcetable','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('ts_timezone','text','false','true','false','Ts Timezone','false');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('geodatainfo_uuid','text','false','true','true','Geodatainfo Uuid','false');

-- Ekstra felterne
INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('id','text','false','true','true','Id','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('noegleord','text','false','true','true','Noegleord','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('uddybende_beskrivelse','multiline','false','true','true','Uddybende Beskrivelse','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('placering','text','false','true','true','Placering','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('placering_qgis','text','false','true','true','Placering Qgis','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('begraensninger_adgang_og_brug','text','false','true','true','Begraensninger Adgang Og Brug','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('ansvarlig_myndighed','text','false','true','true','Ansvarlig Myndighed','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('ansvarligt_kontor','text','false','true','true','Ansvarligt Kontor','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('navn_paa_ansvarlig','text','false','true','true','Navn Paa Ansvarlig','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('e_mail_adresse_paa_ansvarlig','text','false','true','true','E Mail Adresse Paa Ansvarlig','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('telefonnummer_paa_ansvarlig','text','false','true','true','Telefonnummer Paa Ansvarlig','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('uploades_automatisk_kortinfo','text','false','true','true','Uploades Automatisk Kortinfo','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('programmer_hjemmesider_apps_mm','text','false','true','true','Programmer Hjemmesider Apps Mm','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('kilde_t_metadata_besk','text','false','true','true','Kilde T Metadata Besk','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('konfliktsoegning','text','false','true','true','Konfliktsoegning','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('faellesoffentlig_datamodel','text','false','true','true','Faellesoffentlig Datamodel','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('databasekilde','text','false','true','true','Databasekilde','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('gis_sysytem','text','false','true','true','Gis Sysytem','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('kortinfo_url','text','false','true','true','Kortinfo Url','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('ekstern_url','text','false','true','true','Ekstern Url','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('intern_url','text','false','true','true','Intern Url','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('fil_url','text','false','true','true','Fil Url','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('primear_udstiling','text','false','true','true','Primear Udstiling','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('datamodel_url','text','false','true','true','Datamodel Url','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('oprettelses_dato','datetime','false','true','true','Oprettelses Dato','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('aktive','boolean','false','true','true','Aktive','true');

INSERT INTO metadata.gui_table(metadata_col_name, type, required, editable, is_shown, displayname, extra_field)
VALUES ('kan_udstilles','boolean','false','true','true','Kan Udstilles','true');
