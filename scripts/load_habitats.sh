#!/bin/sh

set -e

cd `dirname $0`

echo "Loading habitats"

ogr2ogr -f "PostgreSQL" "PG:host=db user=point_proximity dbname=point_proximity password=devpwd" \
  '/point-proximity/data/woodland.gpkg' \
  -lco PRECISION=no \
  -nln habitats -overwrite \
  -sql "SELECT *, 'woodland' AS type FROM woodland"
echo "Loaded woodland..."

ogr2ogr -f "PostgreSQL" "PG:host=db user=point_proximity dbname=point_proximity password=devpwd" \
  '/point-proximity/data/arable.gpkg' \
  -nln habitats -append \
  -sql "SELECT *, 'arable' AS type FROM arable"
echo "Loaded arable..."

ogr2ogr -f "PostgreSQL" "PG:host=db user=point_proximity dbname=point_proximity password=devpwd" \
  '/point-proximity/data/urban suburban.gpkg' \
  -nln habitats -append \
  -sql "SELECT *, 'urban/suburban' AS type FROM \"urban suburban\""
echo "Loaded urban/suburban..."

ogr2ogr -f "PostgreSQL" "PG:host=db user=point_proximity dbname=point_proximity password=devpwd" \
  '/point-proximity/data/grassland.gpkg' \
  -nln habitats -append \
  -sql "SELECT *, 'grassland' AS type FROM grassland"
echo "Loaded grassland..."

echo "Done!"
