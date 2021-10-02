CREATE DATABASE point_proximity;

\c point_proximity
CREATE EXTENSION postgis;


CREATE USER point_proximity;
ALTER USER point_proximity WITH PASSWORD 'devpwd';
GRANT ALL PRIVILEGES ON DATABASE point_proximity TO point_proximity;

GRANT point_proximity TO postgres;
SET ROLE point_proximity;
