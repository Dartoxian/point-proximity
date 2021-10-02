# Point Proximity

Some geospatial analysis for finding containing regions and for finding ratio of region types near points

Finds the nearest region to a point. Outputs to stdout a csv of the point id to the region type. Additionally
outputs columns with the total area of different region types near a point.

Requirements:

* docker, docker-compose
* poetry https://python-poetry.org/

## Environment setup

* `docker-compose up` will launch the (empty) DB and initialise GDAL
* `poetry install` initialises the local python env


## Loading data

Ensure that the points csv 'all-respondents.cv' is in the `data` dir.
Ensure that the lcm-2017 dataset is available in the `data` dir.

Load point data with `poetry run python ./load_points.py`

Load habitat data with `docker-compose run gdal /point-proximity/scripts/load_habitats.sh`


## Execution

* `poetry run python ./get_respondent_info.py` will print a csv of the processed data.
