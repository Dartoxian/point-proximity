import math

import psycopg2

import multiprocessing

PROXIMITY = 500
KNOWN_HABITAT_TYPES = ["woodland", "arable", "grassland", "urban", "other"]
EXPECTED_AREA_COVERED = math.pow(PROXIMITY, 2) * math.pi
# Allowed quite a generous missing area in case the respondent is near a body of water for exampl
# This obviously breaks down as the proximity increases...
ALLOWED_MISSING_AREA = EXPECTED_AREA_COVERED * 0.5

find_nearest_habitat = f"""
SELECT type
FROM habitats
CROSS JOIN points
WHERE (
  ST_Contains(habitats.geom, ST_Transform(points.location, 27700)) OR
  ST_DWithin(habitats.geom, ST_Transform(points.location, 27700), {PROXIMITY}) 
) 
AND points.respondent_id=%s 
AND habitats.type != 'other'
ORDER BY ST_Distance(habitats.geom, ST_Transform(points.location, 27700)) LIMIT 1;
"""

find_distance_to_habitat_type = f"""
SELECT ST_Distance(habitats.geom, ST_Transform(points.location, 27700))
FROM habitats
LEFT JOIN points ON ST_DWithin(habitats.geom, ST_Transform(points.location, 27700), 10000) 
WHERE points.respondent_id=%s 
AND habitats.type = %s
ORDER BY ST_Distance(habitats.geom, ST_Transform(points.location, 27700)) LIMIT 1;
"""

find_nearby_habitats = f"""
SELECT _mode, type
FROM habitats
CROSS JOIN points
WHERE (
  ST_Contains(habitats.geom, ST_Transform(points.location, 27700)) OR
  ST_DWithin(habitats.geom, ST_Transform(points.location, 27700), {PROXIMITY}) 
) 
AND points.respondent_id=%s 
ORDER BY ST_Distance(habitats.geom, ST_Transform(points.location, 27700));
"""

find_total_area_of_nearby_habitats = f"""
SELECT type, SUM(
    ST_Area(
        ST_Intersection(
            habitats.geom,
            ST_Buffer(ST_Transform(points.location, 27700), {PROXIMITY}, 'quad_segs=32')
        )
    )
) AS area
FROM habitats
LEFT JOIN points ON
  ST_DWithin(habitats.geom, ST_Transform(points.location, 27700), {PROXIMITY}) 
WHERE points.respondent_id=%s 
GROUP BY type;
"""


def get_distance_to_habitat_type(respondent_id: str, habitat_type: str, cur):
    cur.execute(find_distance_to_habitat_type, (respondent_id, habitat_type))
    record = cur.fetchone()
    return round(record[0]) if record is not None else "More than 10km"


def calculate_row(respondent):
    conn = psycopg2.connect("host=localhost dbname=point_proximity user=point_proximity password=devpwd")
    with conn.cursor() as cur:
        cur.execute(find_nearest_habitat, (respondent,))
        nearest_habitat_type = cur.fetchall()
        if len(nearest_habitat_type) != 1:
            cur.execute(find_nearby_habitats, (respondent,))
            nearby_habitats = cur.fetchall()
            raise ValueError(
                f"Respondent {respondent} appears in the wrong number of habitats, "
                f"1 expected but {len(nearest_habitat_type)} found! The nearby habitats (in order)"
                f" are (mode, type) {nearby_habitats}"
            )

        cur.execute(find_total_area_of_nearby_habitats, (respondent,))
        nearby_habitat_types = {r[0]: r[1] for r in cur.fetchall()}
        if abs(sum(nearby_habitat_types.values()) - EXPECTED_AREA_COVERED) > ALLOWED_MISSING_AREA:
            raise ValueError(
                f"Respondent {respondent} calculated nearby habitats seems wrong."
                f"There is {sum(nearby_habitat_types.values()) - EXPECTED_AREA_COVERED} unexplained area,"
                f" which in absolute terms is more than the allowed {ALLOWED_MISSING_AREA}"
            )

        distance_to_nearby_habitat = {
            habitat_type: get_distance_to_habitat_type(respondent, habitat_type, cur)
            if nearest_habitat_type[0][0] != habitat_type
            else 0
            for habitat_type in KNOWN_HABITAT_TYPES
        }

        print(
            f"{respondent},"
            f"{nearest_habitat_type[0][0]},"
            f"{','.join([str(round(nearby_habitat_types.get(t, 0))) for t in KNOWN_HABITAT_TYPES])},",
            f"{','.join([str(distance_to_nearby_habitat.get(t, 0)) for t in KNOWN_HABITAT_TYPES])}",
            flush=True,
        )


if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=point_proximity user=point_proximity password=devpwd")
    with conn.cursor() as cur:
        # Exclude points within the northern ireland envelope
        cur.execute(
            "SELECT respondent_id FROM points "
            "WHERE NOT ST_Contains(ST_MakeEnvelope(-8.1, 53.96, -5.34, 55.36 , 4326), location)"
        )
        respondents = [p[0] for p in cur.fetchall()]

    print(
        f"respondent_id,nearest_habitat,"
        f"{','.join([f'{t}_in_500m2' for t in KNOWN_HABITAT_TYPES])},"
        f"{','.join([f'{t}_distance' for t in KNOWN_HABITAT_TYPES])},"
    )

    pool = multiprocessing.Pool(16)
    pool.map(calculate_row, respondents)
    print("Done!")
