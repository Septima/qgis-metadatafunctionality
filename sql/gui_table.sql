-- These statements create a table and some nescessary data
-- 1: Replace ALL occurrences of [schema] to the schema
-- 2: Replace [owner] to the owner of the metadatatabel
-- 3: Execute these statements in the postgresdatabase

-- Table: metadata.gui_table

CREATE TABLE metadata.gui_table
(
    id SERIAL,
    metadata_col_name character varying NOT NULL,
    type character varying,
    required boolean DEFAULT false,
    editable boolean DEFAULT true,
    is_shown boolean DEFAULT true,
    displayname character varying
    extra_field boolean DEFAULT true,
    CONSTRAINT gui_table_pkey PRIMARY KEY (metadata_col_name)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;

ALTER TABLE [schema].gui_table OWNER to [owner];

-- Insert descriptive fields for the Metadata Model
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('name', 'text', true, true);
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('description', 'text', false, true);
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('geodatainfo_uuid', 'text', false, true);
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('kle_no', 'text', false, true);
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('responsible', 'text', false, true);
INSERT INTO [schema].gui_table(metadata_col_name, type, required, editable) VALUES ('project', 'text', false, true);