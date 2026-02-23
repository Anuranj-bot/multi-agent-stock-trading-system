import psycopg2


def get_connection():
    """
    Creates and returns a connection to TimescaleDB.
    """

    conn = psycopg2.connect(
        host="h87yw4v3gw.rrklcji0qs.tsdb.cloud.timescale.com",
        port="35106",
        database="tsdb",
        user="tsdbadmin",
        password="akfia051wy8ymprn",
        sslmode="require"
    )

    return conn