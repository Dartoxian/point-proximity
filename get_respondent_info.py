import psycopg2

find_nearest_habitat = """
SELECT type, ST_AsText(location), ST_AsGeoJSON(ST_Transform(geom, 4326))
FROM habitats
CROSS JOIN points
WHERE (
  ST_Contains(habitats.geom, ST_Transform(points.location, 27700)) OR
  ST_DWithin(habitats.geom, ST_Transform(points.location, 27700), 1000) 
) 
AND points.respondent_id=%s 
ORDER BY ST_Distance(habitats.geom, ST_Transform(points.location, 27700)) LIMIT 1;
"""


if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=point_proximity user=point_proximity password=devpwd")

    with conn.cursor() as cur:
        cur.execute("SELECT respondent_id FROM points")
        respondents = [p[0] for p in cur.fetchall()]

        for respondent in respondents:
            cur.execute(find_nearest_habitat, (respondent,))
            results = cur.fetchall()
            if len(results) != 1:
                raise ValueError(
                    f"Respondent {respondent} appears in the wrong number of habitats, "
                    f"1 expected but {len(results)} found!"
                )

            print(f"{respondent},{','.join(results[0])}")

    conn.commit()
    print("Done!")
