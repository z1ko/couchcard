#
# Questo script corregge le date nei documenti trasformandole
# in formato ISO-8601
#

import sys
import csv
import tempfile
import shutil

# Nomi delle colonne
columns = [
    "swipe_date",
    "swipe_time",
    "poi_name",
    "poi_device",
    "card_id",
    "card_activation",
    "card_type"
]


# Converte la data e la ritorna YYYY-MM-DD
def iso8601(date):
    parts = date.split('-')
    return f"20{parts[2]}-{parts[1]}-{parts[0]}"


if __name__ == '__main__':

    # Documenti da formattare
    files = [ arg for i, arg in enumerate(sys.argv) if i > 0 ]
    if len(files) == 0:
        print("Usage: python scripts/format.py <files>")
        exit(1)

    total_item_processed = 0
    for file in files:

        temp = tempfile.NamedTemporaryFile("w+t", newline='', delete=False)
        with open(file, 'r', newline='') as csvfile, temp:
            print(f"Processing {file}")

            reader = csv.reader(csvfile)
            writer = csv.writer(temp)

            for i, row in enumerate(reader):
                if i != 0: 

                    row[0] = iso8601(row[0]) # Data striciata
                    row[5] = iso8601(row[5]) # Data attivazione VeronaCard
                    del row[6:8] # colonne di dubbia utilità

                    writer.writerow(row)
                    total_item_processed += 1

                else:
                    writer.writerow(columns)
                
        # Sovrascrive vecchio file
        shutil.move(temp.name, file)

    print(f"Processed items: {total_item_processed}")