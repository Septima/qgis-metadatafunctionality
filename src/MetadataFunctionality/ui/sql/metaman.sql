CREATE TABLE "metaman" (
	"resp_center_off" varchar,
	"beskrivelse" varchar,
	"name" varchar,
	"timestamp" varchar,
	"proj_wor" varchar,
	"journal_nr" varchar,
	"guid" varchar,
	"host" varchar,
	"db" varchar,
	"port" int,
	"schema" varchar,
	"table" varchar,
	"ts" timestamp without time zone default (now() at time zone 'utc')
)
WITH (OIDS=FALSE);
ALTER TABLE "metaman" OWNER TO "metaman";