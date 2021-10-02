import psycopg2
import csv

if __name__ == "__main__":
    conn = psycopg2.connect("host=localhost dbname=point_proximity user=point_proximity password=devpwd")

    with open("data/all-respondents.csv", "r") as csvfile:
        points = list(csv.DictReader(csvfile))
        print(f"Loaded {len(points)} points")
        points = [p for p in points if p["Latitude"] != "FAILED"]
        print(f"{len(points)} are valid")

    with conn.cursor() as cur:
        cur.execute("DROP TABLE IF EXISTS points;")
        cur.execute("CREATE TABLE points(respondent_id text PRIMARY KEY, address text);")
        cur.execute("SELECT AddGeometryColumn ('public', 'points', 'location', 4326, 'POINT',2);")
        cur.execute("CREATE INDEX ON points USING GIST(location);")

        # Load data
        for point in points:
            cur.execute(
                "INSERT INTO points VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326))",
                (point["Responded ID"], point["Address"], point["Longitude"], point["Latitude"]),
            )

    conn.commit()
    print("Points Loaded!")
