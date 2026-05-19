#!/usr/bin/env python
# coding: utf-8

import sqlite3

import numpy as np
from PIL import Image
from tqdm import tqdm
from ultralytics import YOLO

model = YOLO('best_birds_2025_models/birds-2025-classify-v45.pt')

conn = sqlite3.connect('results.db')
cur = conn.cursor()

cur.execute("PRAGMA table_info(detections)")
columns = [col[1] for col in cur.fetchall()]
if "class_name" not in columns:
    cur.execute("ALTER TABLE detections ADD COLUMN class_name TEXT")
if "class_confidence" not in columns:
    cur.execute("ALTER TABLE detections ADD COLUMN class_confidence REAL")
conn.commit()

cur.execute("SELECT rowid, file, x1, y1, x2, y2 FROM detections")
rows = cur.fetchall()

buffer = []
error_buffer = []
names = model.names

for i, (rowid, file, x1, y1, x2, y2) in enumerate(tqdm(rows)):
    try:
        image = Image.open(file).convert("RGB")
        crop = image.crop((int(x1), int(y1), int(x2), int(y2)))

        result = model(np.array(crop), verbose=False)
        probs = result[0].probs
        if probs is None:
            error_buffer.append((file, "no detection"))
            continue

        top_class_id = int(probs.top1)
        class_name = names[top_class_id]
        confidence = float(probs.data[top_class_id])

        buffer.append((class_name, confidence, rowid))

    except Exception as e:
        error_buffer.append((file, str(e)))
        continue

    if (i + 1) % 1000 == 0:
        if buffer:
            cur.executemany(
                """
                UPDATE detections
                SET class_name = ?, class_confidence = ?
                WHERE rowid = ?
            """, buffer)
            buffer = []

        if error_buffer:
            cur.executemany(
                """
                INSERT INTO errors (file, error) VALUES (?, ?)
            """, error_buffer)
            error_buffer = []

        conn.commit()

if buffer:
    cur.executemany(
        """
        UPDATE detections
        SET class_name = ?, class_confidence = ?
        WHERE rowid = ?
    """, buffer)

if error_buffer:
    cur.executemany(
        """
        INSERT INTO errors (file, error) VALUES (?, ?)
    """, error_buffer)

conn.commit()
conn.close()
