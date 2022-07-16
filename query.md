# Generazione collezioni

I dati vengono caricati direttamente da csv nella collezione Couchcard.data.swipes, da qui vengono processati e inseriti nelle due collezioni 'days' e 'cards' che mantengono gli stessi dati con pattern di accesso specializzati per le query date.

## Days

Le swipes vengono suddivise per giorno e per poi.

```
INSERT INTO Couchcard.data.pois (KEY poi_name)
SELECT poi_name, ARRAY_AGG(DISTINCT poi_device) AS devices
FROM Couchcard.data.swipes
GROUP BY poi_name;
```

```
INSERT INTO Couchcard.data.days (KEY day)
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
UPSERT INTO Couchcard.data.cards (KEY card)
SELECT S.card_id AS card, S.card_activation AS activation, S.card_type AS type, 
       ARRAY_AGG({ S.poi_name, S.swipe_time, S.swipe_date, S.poi_device }) AS swipes
FROM Couchcard.data.swipes S
WHERE S.card_id IS NOT NULL
GROUP BY S.card_id, S.card_activation, S.card_type;
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
SELECT META(C).id AS card, S.swipe_date, ARRAY_AGG({ S.poi_device, S.poi_name, S.swipe_time }) AS swipes, COUNT(*) AS swipe_count
FROM Couchcard.data.cards C UNNEST C.swipes S
WHERE C.type = "vrcard-24-2019"
GROUP BY META(C).id, S.swipe_date
HAVING COUNT(*) > 3;
```