#!/bin/sh

set -e

cd `dirname $0`

echo "Loading habitats"

ogr2ogr -f "PostgreSQL" "PG:host=db user=point_proximity dbname=point_proximity password=devpwd" \
  '/point-proximity/data/lcm-2017-vec_4164463/lcm-2017-vec_4164463.gpkg' \
  -lco PRECISION=no \
  -nln habitats -overwrite \
  -sql "SELECT *,
       CASE _mode
        WHEN 1 THEN 'woodland'
        WHEN 2 THEN 'woodland'
        WHEN 3 THEN 'arable'
        WHEN 4 THEN 'grassland'
        WHEN 5 THEN 'grassland'
        WHEN 6 THEN 'grassland'
        WHEN 7 THEN 'grassland'
        WHEN 10 THEN 'grassland'
        WHEN 20 THEN 'urban'
        WHEN 21 THEN 'urban'
        ELSE 'other'
       END AS type
      FROM lcm_2017"
echo "Loaded habitats..."


echo "Done!"
