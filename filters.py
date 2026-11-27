"""Construcción de consultas para MongoDB (búsqueda y filtros de /movies).

HU-07: búsqueda por título

"""
import re


def clean_term(q):
    """Devuelve el término sin espacios sobrantes ('' si viene vacío o None)."""
    return (q or "").strip()


def build_query(q=None):
    """Construye la consulta para MongoDB a partir de los parámetros de búsqueda y filtros."""
    query = {}
    term = clean_term(q)
    if term:
        query["title"] = {"$regex": re.escape(term), "$options": "i"}

    return query