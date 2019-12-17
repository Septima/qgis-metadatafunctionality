-- These statements create a table and a function
-- 1: Replace ALL occurrences of [schema].[table] to the schema and name of the metadatatable
-- 2: Replace [owner] to the owner of the metadatatabel
-- 3: Execute these statements in the postgresdatabase

CREATE TABLE [schema].[table] (
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
    geodatainfo_uuid uuid,
    CONSTRAINT pk_metadata PRIMARY KEY (guid)
)
WITH (OIDS=FALSE);
ALTER TABLE [schema].[table] OWNER TO [owner];

create or replace function [schema]._getMetaDataMatches(varchar, int default 1000)
returns table (name varchar, description varchar, host varchar, db varchar, port integer, schema varchar, sourcetable varchar)
    as $$
    WITH QUERY AS (
                SELECT $1::text AS VALUE
            ),
            st AS (
                SELECT REGEXP_SPLIT_TO_TABLE(value, E'\\s+') search_token
                FROM QUERY
            )
            SELECT
              name,
              description,
              host,
              db,
              port,
              schema,
              sourcetable
            FROM [schema].[table] m1
            WHERE NOT EXISTS
            (
                SELECT *
                FROM st
                WHERE NOT EXISTS
                (
                    SELECT 1
                    FROM [schema].[table] m2
                    WHERE
                    (
                        m2.responsible ILIKE search_token
                        OR m2.description ILIKE '%' || search_token || '%'
                        OR m2.name ILIKE search_token || '%'
                        OR m2.db ILIKE search_token
                        OR m2.sourcetable ILIKE search_token || '%'
                        OR m2.project ILIKE '%' || search_token || '%'
                    )
                AND m1.guid = m2.guid
                )
            )
            LIMIT $2;
    $$
    language sql;