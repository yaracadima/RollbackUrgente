import re
from filters import build_query, clean_term
"""pruebas para los filtros de búsqueda"""

def matches(query, title):
    cond = query.get("title")
    if cond is None:
        return True
    flags = re.I if "i" in cond["$options"] else 0
    return re.search(cond["$regex"], title, flags) is not None


def test_sin_termino_trae_todo():
    assert build_query() == {}
    assert build_query("") == {}
    assert build_query("   ") == {}


def test_parcial_y_sin_mayusculas():
    q = build_query("mAt")
    assert matches(q, "The Matrix")
    assert not matches(q, "Titanic")


def test_espacios_se_recortan():
    assert clean_term("  Matrix ") == "Matrix"


def test_caracteres_especiales_son_literales():
    q = build_query("(2)")
    assert matches(q, "Toy Story (2)")
    assert not matches(q, "Toy Story 2")