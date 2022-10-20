# Generazione collezioni

I dati vengono caricati direttamente da csv nella collezione 'swipes', da qui vengono processati e inseriti nelle due collezioni 'days' e 'cards' che mantengono gli stessi dati con pattern di accesso specializzati per le query date.

Queste trasformazioni iniziali richiedono un indice primario per le 'swipes', creato in questo modo:

```
CREATE PRIMARY INDEX idx_swipes ON Couchcard.data.swipes;
```

## Days

Le swipes vengono suddivise per giorno e per poi.

```
-- Collection: Couchcard.data.pois
UPSERT INTO Couchcard.data.pois (KEY poi_name)
SELECT poi_name, ARRAY_AGG(DISTINCT poi_device) AS devices
FROM Couchcard.data.swipes
GROUP BY poi_name;
```

```
-- Collection: Couchcard.data.days
UPSERT INTO Couchcard.data.days (KEY day)
SELECT G.swipe_date AS day, ARRAY_AGG({G.poi, G.swipes}) as pois
FROM (
    SELECT S.swipe_date, S.poi_name AS poi, ARRAY_AGG({ S.swipe_time, S.card_id, S.poi_device }) as swipes
    FROM Couchcard.data.swipes S
    GROUP BY S.swipe_date, S.poi_name
    ORDER BY S.poi_name
) AS G
GROUP BY G.swipe_date
ORDER BY G.swipe_date;
```

## Cards

Le swipes vengono suddivise per VeronaCard ID.

```
-- Collection: Couchcard.data.cards
UPSERT INTO couchcard.data.cards (KEY id)
SELECT G.card_type AS type, G.card_id AS id, ARRAY_AGG({G.date, G.swipes, G.swipes_count}) AS dates
FROM (
    SELECT S.card_type, S.card_id, S.swipe_date AS date, ARRAY_AGG({ S.swipe_time, S.poi_name, S.poi_device}) AS swipes, COUNT(S.swipe_time) AS swipes_count
    FROM couchcard.data.swipes S
    GROUP BY S.card_type, S.card_id, S.swipe_date
) AS G
GROUP BY G.card_type, G.card_id;
```

# Interrogazioni

Per ogni giorno del mese trovare il numero totale di accessi ai POI

```
SELECT AP.poi, AP.day, IFMISSINGORNULL(CNT.counter, 0) AS counter
FROM (
    -- Ottiene tutte le coppie (Giorno, POI) estraibili dai dati
    SELECT META(P).id AS poi, DS.day
    FROM Couchcard.data.pois P, (
        SELECT META(D).id as day
        FROM Couchcard.data.days D
        WHERE META(D).id BETWEEN "2020-01-01" AND "2020-02-01"
    ) AS DS
) AS AP LEFT JOIN (
    -- Ottiene tutte le coppie (Giorno, POI) presenti e il numero associato di swipes
    SELECT META(D).id AS day, P.poi, ARRAY_COUNT(P.swipes) AS counter
    FROM Couchcard.data.days AS D UNNEST D.pois P
    WHERE META(D).id BETWEEN "2020-01-01" AND "2020-02-01"
) AS CNT
ON AP.poi = CNT.poi AND AP.day = CNT.day;
```

In un giorno del mese trovare POI con numero massimo e minimo di accessi

```
-- Ottiene un ordinamento di tutti gli insiemi di POIs con lo stesso numero di accessi un giorno
WITH POIGRPS AS (
    SELECT RES.swipes, ARRAY_AGG(RES.poi) AS pois
    FROM (
        -- Conta il numero di accessi ad un POI, anche se questo non appare nella giornata
        SELECT META(ALLPOI).id as poi, IFMISSINGORNULL(CNT.swipes, 0) AS swipes
        FROM Couchcard.data.pois ALLPOI LEFT JOIN (
            SELECT P.poi, ARRAY_COUNT(P.swipes) AS swipes
            FROM Couchcard.data.days D UNNEST D.pois P
            WHERE META(D).id BETWEEN "2020-03-03" AND "2020-03-04"
        ) AS CNT
        ON META(ALLPOI).id = CNT.poi
    ) AS RES
    GROUP BY RES.swipes
)
SELECT MAXIM.swipes AS max_swipes, 
       MAXIM.pois   AS max_pois, 
       MINIM.swipes AS min_swipes, 
       MINIM.pois   AS min_pois
FROM (
    SELECT PG.swipes, PG.pois FROM POIGRPS PG
    ORDER BY PG.swipes DESC
    LIMIT 1
) AS MAXIM, (
    SELECT PG.swipes, PG.pois FROM POIGRPS PG
    ORDER BY PG.swipes ASC
    LIMIT 1
) AS MINIM;
```

Dato un profilo VC, trovare i codici delle VC di quel profilo con almeno 3 strisciate in un giorno, riportandole tutte e 3

```
SELECT C.id, D.date, ARRAY_AGG({S.swipe_time, S.poi_name, S.poi_device}) AS swipes
FROM couchcard.data.cards C UNNEST C.dates D UNNEST D.swipes S
WHERE D.swipes_count >= 3
GROUP BY C.id, D.date;
```

viene usato il seguente indice sugli array per velocizzare l'accesso

```
CREATE INDEX sidx_cards_swipes ON couchcard.data.cards (
    ALL ARRAY (
        ALL ARRAY D.swipes_count FOR S IN D.swipes END
    ) FOR D IN dates END
);
```