class SqlQueries:

    drop_query = "DROP TABLE IF EXISTS {table};"

    staging_events_table_create = ("""
        CREATE TABLE {table} (
            artist              character varying(200)  ,
            auth                character varying(10)   ,
            firstName           character varying(200)  ,
            gender              character varying(1)    ,
            itemInSession       integer                 ,
            lastName            character varying(200)  ,
            length              double precision        ,
            level               character varying(10)   ,
            location            character varying(200)  ,
            method              character varying(10)   ,
            page                character varying(20)   ,
            registration        double precision        ,
            sessionId           integer                 ,
            song                character varying(200)  ,
            status              integer                 ,
            ts                  bigint                  ,
            userAgent           character varying(200)  ,
            userId              character varying(18)
        );
    """)

    staging_songs_table_create = ("""
        CREATE TABLE {table} (
            num_songs           bigint                  ,
            artist_id           character varying(18)   ,
            artist_latitude     double precision        ,
            artist_longitude    double precision        ,
            artist_location     character varying(200)  ,
            artist_name         character varying(200)  ,
            song_id             character varying(18)   ,
            title               character varying(200)  ,
            duration            double precision        ,
            year                integer
        );
    """)


    staging_insert_query = ("""
        copy {table} from '{bucket}'
        credentials 'aws_iam_role={arn}'
        json 'auto ignorecase'
        region 'us-west-2';
    """)

    songplay_table_insert = ("""
        SELECT
                md5(events.sessionid || events.start_time) songplay_id,
                events.start_time,
                events.userid,
                events.level,
                songs.song_id,
                songs.artist_id,
                events.sessionid,
                events.location,
                events.useragent
                FROM (SELECT TIMESTAMP 'epoch' + ts/1000 * interval '1 second' AS start_time, *
            FROM staging_events
            WHERE page='NextSong') events
            LEFT JOIN staging_songs songs
            ON events.song = songs.title
                AND events.artist = songs.artist_name
                AND events.length = songs.duration
    """)

    user_table_insert = ("""
        SELECT distinct userid, firstname, lastname, gender, level
        FROM staging_events
        WHERE page='NextSong'
    """)

    song_table_insert = ("""
        SELECT distinct song_id, title, artist_id, year, duration
        FROM staging_songs
    """)

    artist_table_insert = ("""
        SELECT distinct artist_id, artist_name, artist_location, artist_latitude, artist_longitude
        FROM staging_songs
    """)

    time_table_insert = ("""
        SELECT start_time, extract(hour from start_time), extract(day from start_time), extract(week from start_time),
               extract(month from start_time), extract(year from start_time), extract(dayofweek from start_time)
        FROM songplays
    """)
