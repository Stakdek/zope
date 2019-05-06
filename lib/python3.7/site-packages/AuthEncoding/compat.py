import six

if six.PY3:
    long = int
else:
    long = long


def b(arg):
    """Convert `arg` to bytes."""
    if isinstance(arg, six.text_type):
        arg = arg.encode("latin-1")
    return arg


def u(arg):
    """Convert `arg` to text."""
    if isinstance(arg, six.binary_type):
        arg = arg.decode('ascii', 'replace')
    return arg
