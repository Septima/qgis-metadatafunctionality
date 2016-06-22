CREATE TABLE schema.metadata (
    "name" varchar,
    "beskrivelse" varchar,
    "journal_nr" varchar,
    "resp_center_off" varchar,
    "proj_wor" varchar,
    "host" varchar,
    "db" varchar,
    "port" int,
    "schema" varchar,
    "table" varchar,
    "guid" varchar,
    "timestamp" varchar,
    "ts" timestamp without time zone default (now() at time zone 'utc')
)
WITH (OIDS=FALSE);
ALTER TABLE schema.metadata OWNER TO owner;