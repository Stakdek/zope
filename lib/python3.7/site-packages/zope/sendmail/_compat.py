try:
    text_type = unicode
    PY2 = True     # pragma: PY2
except NameError:  # pragma: PY3
    text_type = str
    PY2 = False
