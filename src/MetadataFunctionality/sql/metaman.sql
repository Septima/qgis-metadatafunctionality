/*
 Navicat PostgreSQL Data Transfer

 Source Server         : localhost
 Source Server Version : 90405
 Source Host           : localhost
 Source Database       : amagerfaelled
 Source Schema         : public

 Target Server Version : 90405
 File Encoding         : utf-8

 Date: 04/13/2016 10:55:38 AM
*/

-- ----------------------------
--  Table structure for metaman
-- ----------------------------
DROP TABLE IF EXISTS "metaman";
CREATE TABLE "metaman" (
	"resp_center_off" varchar COLLATE "default",
	"beskrivelse" varchar COLLATE "default",
	"name" varchar COLLATE "default",
	"timestamp" varchar COLLATE "default",
	"proj_wor" varchar COLLATE "default",
	"table" varchar COLLATE "default",
	"journal_nr" varchar COLLATE "default",
	"guid" varchar COLLATE "default",
	"db" varchar COLLATE "default",
	"schema" varchar COLLATE "default"
)
WITH (OIDS=FALSE);
ALTER TABLE "metaman" OWNER TO "besn";

