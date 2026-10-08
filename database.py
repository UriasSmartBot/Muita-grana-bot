import os
import sqlite3
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", "signals.sqlite3")


def conectar():
    caminho = Path(DB_PATH)
    caminho.parent.mkdir(parents=True, exist_ok=True)

    con = sqlite3.connect(str(caminho), timeout=30)
    con.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            analysis_time INTEGER NOT NULL,
            entry_time INTEGER NOT NULL,
            score INTEGER NOT NULL,
            entry_price REAL,
            expiry_price REAL,
            outcome TEXT DEFAULT 'PENDING',
            UNIQUE(symbol, analysis_time)
        )
    """)
    con.commit()
    return con


def salvar_sinal(symbol, side, analysis_time, entry_time, score):
    with conectar() as con:
        cursor = con.execute("""
            INSERT OR IGNORE INTO signals
            (symbol, side, analysis_time, entry_time, score)
            VALUES (?, ?, ?, ?, ?)
        """, (symbol, side, analysis_time, entry_time, score))
        return cursor.rowcount == 1


def registrar_entrada(signal_id, price):
    with conectar() as con:
        con.execute(
            "UPDATE signals SET entry_price = ? WHERE id = ?",
            (price, signal_id)
        )


def registrar_resultado(signal_id, price, outcome):
    if outcome not in ("WIN", "LOSS", "DRAW"):
        raise ValueError("Resultado inválido")

    with conectar() as con:
        con.execute("""
            UPDATE signals
            SET expiry_price = ?, outcome = ?
            WHERE id = ?
        """, (price, outcome, signal_id))


def obter_estatisticas():
    with conectar() as con:
        return con.execute("""
            SELECT
                COUNT(*),
                SUM(outcome = 'WIN'),
                SUM(outcome = 'LOSS'),
                SUM(outcome = 'DRAW'),
                SUM(outcome = 'PENDING')
            FROM signals
        """).fetchone()
