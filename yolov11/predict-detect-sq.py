import json
import sqlite3

from tqdm import tqdm
from ultralytics import YOLO

with open('files.json') as j:
    files = json.load(j)

model = YOLO('birds-2025-detect-v3-best.pt')

conn = sqlite3.connect('results.db')
cur = conn.cursor()

cur.execute('''
CREATE TABLE IF NOT EXISTS detections (
    file TEXT,
    name TEXT,
    class INTEGER,
    confidence REAL,
    x1 REAL,
    y1 REAL,
    x2 REAL,
    y2 REAL
)
''')

cur.execute('''
CREATE TABLE IF NOT EXISTS errors (
    file TEXT,
    error TEXT
)
''')
conn.commit()

cur.execute('SELECT DISTINCT file FROM detections')
processed_files = set(row[0] for row in cur.fetchall())

unprocessed_files = [file for file in files if file not in processed_files]

buffer = []
for i, file in enumerate(tqdm(unprocessed_files)):
    try:
        preds = model(file)
        for pred in preds:
            result = json.loads(pred.to_json())
            for item in result:
                buffer.append(
                    (file, item['name'], item['class'], item['confidence'],
                     item['box']['x1'], item['box']['y1'], item['box']['x2'],
                     item['box']['y2']))
    except Exception as e:
        cur.execute('INSERT INTO errors (file, error) VALUES (?, ?)',
                    (file, str(e)))
        conn.commit()
        continue

    if (i + 1) % 1000 == 0:
        cur.executemany(
            '''
            INSERT INTO detections (file, name, class, confidence, x1, y1, x2, y2)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', buffer)
        conn.commit()
        buffer = []

if buffer:
    cur.executemany(
        '''
        INSERT INTO detections (file, name, class, confidence, x1, y1, x2, y2)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', buffer)
    conn.commit()

conn.close()
