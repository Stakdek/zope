from threading import local


# a thread-local object holding arbitrary data
localData = local()
marker = []


# helper functions to get/set local values or optionally initialize them
def getLocal(name, factory=lambda: None):
    value = getattr(localData, name, marker)
    if value is marker:
        value = factory()
        setLocal(name, value)
    return value


def setLocal(name, value):
    setattr(localData, name, value)
