/*****************************************************************************

  Copyright (c) 2001, 2002 Zope Foundation and Contributors.
  All Rights Reserved.

  This software is subject to the provisions of the Zope Public License,
  Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  FOR A PARTICULAR PURPOSE

****************************************************************************/

/* Strings initialized by init_strings() below. */
static PyObject *py___slotnames__, *copy_reg_slotnames, *__newobj__;
static PyObject *py___getnewargs__, *py___getstate__;


static int
pickle_setup(void)
{
    PyObject* copy_reg;

#define INIT_STRING(S) if (!(py_ ## S = INTERN(#S))) return -1;
    INIT_STRING(__slotnames__);
    INIT_STRING(__getnewargs__);
    INIT_STRING(__getstate__);
#undef INIT_STRING

#ifdef PY3K
    copy_reg = PyImport_ImportModule("copyreg");
#else
    copy_reg = PyImport_ImportModule("copy_reg");
#endif

    if (!copy_reg) {
        return -1;
    }

    copy_reg_slotnames = PyObject_GetAttrString(copy_reg, "_slotnames");
    if (!copy_reg_slotnames)
    {
      Py_DECREF(copy_reg);
      return -1;
    }

    __newobj__ = PyObject_GetAttrString(copy_reg, "__newobj__");
    if (!__newobj__)
    {
      Py_DECREF(copy_reg);
      return -1;
    }

  return 0;
}

static PyObject * pickle_slotnames(PyTypeObject *cls);
static PyObject * convert_name(PyObject *name);



/****************************************************************************/


static PyObject *
pickle_slotnames(PyTypeObject *cls)
{
    PyObject *slotnames;

    slotnames = PyDict_GetItem(cls->tp_dict, py___slotnames__);
    if (slotnames)
    {
        int n = PyObject_Not(slotnames);
        if (n < 0)
            return NULL;
        if (n)
            slotnames = Py_None;

        Py_INCREF(slotnames);
        return slotnames;
    }

    slotnames = PyObject_CallFunctionObjArgs(copy_reg_slotnames,
                                            (PyObject*)cls, NULL);
    if (slotnames && !(slotnames == Py_None || PyList_Check(slotnames)))
    {
        PyErr_SetString(PyExc_TypeError,
                        "copy_reg._slotnames didn't return a list or None");
        Py_DECREF(slotnames);
        return NULL;
    }

    return slotnames;
}

static PyObject *
pickle_copy_dict(PyObject *state)
{
    PyObject *copy, *key, *value;
    char *ckey;
    Py_ssize_t pos = 0;

    copy = PyDict_New();
    if (!copy)
        return NULL;

    if (!state)
        return copy;

    while (PyDict_Next(state, &pos, &key, &value))
    {
        int is_special;
#ifdef PY3K
        if (key && PyUnicode_Check(key))
        {
            PyObject *converted = convert_name(key);
            ckey = PyBytes_AS_STRING(converted);
#else
        if (key && PyBytes_Check(key))
        {
            ckey = PyBytes_AS_STRING(key);
#endif
            is_special = (*ckey == '_' &&
                          (ckey[1] == 'v' || ckey[1] == 'p') &&
                           ckey[2] == '_');
#ifdef PY3K
            Py_DECREF(converted);
#endif
            if (is_special) /* skip volatile and persistent */
                continue;
        }

        if (PyObject_SetItem(copy, key, value) < 0)
            goto err;
    }

    return copy;
err:
    Py_DECREF(copy);
    return NULL;
}


static char pickle___getstate__doc[] =
  "Get the object serialization state\n"
  "\n"
  "If the object has no assigned slots and has no instance dictionary, then \n"
  "None is returned.\n"
  "\n"
  "If the object has no assigned slots and has an instance dictionary, then \n"
  "the a copy of the instance dictionary is returned. The copy has any items \n"
  "with names starting with '_v_' or '_p_' ommitted.\n"
  "\n"
  "If the object has assigned slots, then a two-element tuple is returned.  \n"
  "The first element is either None or a copy of the instance dictionary, \n"
  "as described above. The second element is a dictionary with items \n"
  "for each of the assigned slots.\n"
  ;

static PyObject *
pickle___getstate__(PyObject *self)
{
    PyObject *slotnames=NULL, *slots=NULL, *state=NULL;
    PyObject **dictp;
    int n=0;

    slotnames = pickle_slotnames(Py_TYPE(self));
    if (!slotnames)
        return NULL;

    dictp = _PyObject_GetDictPtr(self);
    if (dictp)
        state = pickle_copy_dict(*dictp);
    else
    {
        state = Py_None;
        Py_INCREF(state);
    }

    if (slotnames != Py_None)
    {
        int i;

        slots = PyDict_New();
        if (!slots)
            goto end;

        for (i = 0; i < PyList_GET_SIZE(slotnames); i++)
        {
            PyObject *name, *value;
            char *cname;
            int is_special;

            name = PyList_GET_ITEM(slotnames, i);
#ifdef PY3K
            if (PyUnicode_Check(name))
            {
                PyObject *converted = convert_name(name);
                cname = PyBytes_AS_STRING(converted);
#else
            if (PyBytes_Check(name))
            {
                cname = PyBytes_AS_STRING(name);
#endif
                is_special = (*cname == '_' &&
                              (cname[1] == 'v' || cname[1] == 'p') &&
                               cname[2] == '_');
#ifdef PY3K
                Py_DECREF(converted);
#endif
                if (is_special) /* skip volatile and persistent */
                {
                    continue;
                }
            }

            /* Unclear:  Will this go through our getattr hook? */
            value = PyObject_GetAttr(self, name);
            if (value == NULL)
                PyErr_Clear();
            else
            {
                int err = PyDict_SetItem(slots, name, value);
                Py_DECREF(value);
                if (err < 0)
                    goto end;
                n++;
            }
        }
    }

    if (n)
        state = Py_BuildValue("(NO)", state, slots);

end:
    Py_XDECREF(slotnames);
    Py_XDECREF(slots);

    return state;
}

static int
pickle_setattrs_from_dict(PyObject *self, PyObject *dict)
{
    PyObject *key, *value;
    Py_ssize_t pos = 0;

    if (!PyDict_Check(dict))
    {
        PyErr_SetString(PyExc_TypeError, "Expected dictionary");
        return -1;
    }

    while (PyDict_Next(dict, &pos, &key, &value))
    {
        if (PyObject_SetAttr(self, key, value) < 0)
            return -1;
    }
    return 0;
}

static char pickle___setstate__doc[] =
  "Set the object serialization state\n\n"
  "The state should be in one of 3 forms:\n\n"
  "- None\n\n"
  "  Ignored\n\n"
  "- A dictionary\n\n"
  "  In this case, the object's instance dictionary will be cleared and \n"
  "  updated with the new state.\n\n"
  "- A two-tuple with a string as the first element. \n\n"
  "  In this case, the method named by the string in the first element will\n"
  "  be called with the second element.\n\n"
  "  This form supports migration of data formats.\n\n"
  "- A two-tuple with None or a Dictionary as the first element and\n"
  "  with a dictionary as the second element.\n\n"
  "  If the first element is not None, then the object's instance dictionary \n"
  "  will be cleared and updated with the value.\n\n"
  "  The items in the second element will be assigned as attributes.\n"
  ;

static PyObject *
pickle___setstate__(PyObject *self, PyObject *state)
{
    PyObject *slots=NULL;

    if (PyTuple_Check(state))
    {
        if (!PyArg_ParseTuple(state, "OO:__setstate__", &state, &slots))
            return NULL;
    }

    if (state != Py_None)
    {
        PyObject **dict;
        PyObject *d_key, *d_value;
        Py_ssize_t i;

        dict = _PyObject_GetDictPtr(self);
        
        if (!dict)
        {
            PyErr_SetString(PyExc_TypeError,
                            "this object has no instance dictionary");
            return NULL;
        }

        if (!*dict)
        {
            *dict = PyDict_New();
            if (!*dict)
                return NULL;
        }

        PyDict_Clear(*dict);

        i = 0;
        while (PyDict_Next(state, &i, &d_key, &d_value)) {
            /* normally the keys for instance attributes are
               interned.  we should try to do that here. */
            if (NATIVE_CHECK_EXACT(d_key)) {
                Py_INCREF(d_key);
                INTERN_INPLACE(&d_key);
                Py_DECREF(d_key);
            }
            if (PyObject_SetItem(*dict, d_key, d_value) < 0)
                return NULL;
        }
    }

    if (slots && pickle_setattrs_from_dict(self, slots) < 0)
        return NULL;

    Py_INCREF(Py_None);
    return Py_None;
}

static char pickle___reduce__doc[] =
  "Reduce an object to contituent parts for serialization\n"
  ;

static PyObject *
pickle___reduce__(PyObject *self)
{
    PyObject *args=NULL, *bargs=NULL, *state=NULL, *getnewargs=NULL;
    int l, i;

    getnewargs = PyObject_GetAttr(self, py___getnewargs__);
    if (getnewargs)
    {
        bargs = PyObject_CallFunctionObjArgs(getnewargs, NULL);
        Py_DECREF(getnewargs);
        if (!bargs)
            return NULL;
        l = PyTuple_Size(bargs);
        if (l < 0)
            goto end;
    }
    else
    {
        PyErr_Clear();
        l = 0;
    }

    args = PyTuple_New(l+1);
    if (args == NULL)
        goto end;

    Py_INCREF(Py_TYPE(self));
    PyTuple_SET_ITEM(args, 0, (PyObject*)(Py_TYPE(self)));
    for (i = 0; i < l; i++)
    {
        Py_INCREF(PyTuple_GET_ITEM(bargs, i));
        PyTuple_SET_ITEM(args, i+1, PyTuple_GET_ITEM(bargs, i));
    }

    state = PyObject_CallMethodObjArgs(self, py___getstate__, NULL);
    if (!state)
        goto end;

    state = Py_BuildValue("(OON)", __newobj__, args, state);

end:
    Py_XDECREF(bargs);
    Py_XDECREF(args);

    return state;
}

/* convert_name() returns a new reference to a string name
   or sets an exception and returns NULL.
*/

static PyObject *
convert_name(PyObject *name)
{
#ifdef Py_USING_UNICODE
  /* The Unicode to string conversion is done here because the
     existing tp_setattro slots expect a string object as name
     and we wouldn't want to break those. */
    if (PyUnicode_Check(name))
    {
        name = PyUnicode_AsEncodedString(name, NULL, NULL);
    }
    else
#endif
        if (!PyBytes_Check(name))
        {
            PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
            return NULL;
        }
        else
            Py_INCREF(name);
    return name;
}

#define PICKLE_GETSTATE_DEF \
{"__getstate__", (PyCFunction)pickle___getstate__, METH_NOARGS,      \
   pickle___getstate__doc},

#define PICKLE_SETSTATE_DEF \
{"__setstate__", (PyCFunction)pickle___setstate__, METH_O,           \
   pickle___setstate__doc},                                          

#define PICKLE_GETNEWARGS_DEF

#define PICKLE_REDUCE_DEF \
{"__reduce__", (PyCFunction)pickle___reduce__, METH_NOARGS,          \
   pickle___reduce__doc},

#define PICKLE_METHODS PICKLE_GETSTATE_DEF PICKLE_SETSTATE_DEF \
                       PICKLE_GETNEWARGS_DEF PICKLE_REDUCE_DEF
