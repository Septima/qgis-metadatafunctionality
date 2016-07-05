CREATE TABLE schema.metadata (
    name varchar,
    description varchar,
    kle_no varchar,
    responsible varchar,
    project varchar,
    host varchar,
    db varchar,
    port int,
    schema varchar,
    sourcetable varchar,
    guid varchar,
    ts_timezone varchar,
    CONSTRAINT pk_metadata PRIMARY KEY (guid)
)
WITH (OIDS=FALSE);
ALTER TABLE schema.metadata OWNER TO owner;