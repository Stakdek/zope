/*

 Copyright (c) 2003 Zope Foundation and Contributors.
 All Rights Reserved.

 This software is subject to the provisions of the Zope Public License,
 Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
 THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
 WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
 WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
 FOR A PARTICULAR PURPOSE.

*/
static char _Persistence_module_documentation[] =
"Persistent ExtensionClass\n"
;

#include "ExtensionClass/ExtensionClass.h"
#include "ExtensionClass/_compat.h"
#include "persistent/cPersistence.h"


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
    if (PyUnicode_Check(name)) {
		name = PyUnicode_AsEncodedString(name, NULL, NULL);
    }
    else
#endif
    if (!NATIVE_CHECK(name)) {
		PyErr_SetString(PyExc_TypeError, "attribute name must be a string");
	return NULL;
    } else
		Py_INCREF(name);
    return name;
}

/* Returns true if the object requires unghostification.

   There are several special attributes that we allow access to without
   requiring that the object be unghostified:
   __class__
   __del__
   __dict__
   __of__
   __setstate__
*/

static int
unghost_getattr(const char *s)
{
    if (*s++ != '_')
	return 1;
    if (*s == 'p') {
	s++;
	if (*s == '_')
	    return 0; /* _p_ */
	else
	    return 1;
    }
    else if (*s == '_') {
	s++;
	switch (*s) {
	case 'c':
	    return strcmp(s, "class__");
	case 'd':
	    s++;
	    if (!strcmp(s, "el__"))
		return 0; /* __del__ */
	    if (!strcmp(s, "ict__"))
		return 0; /* __dict__ */
	    return 1;
	case 'o':
	    return strcmp(s, "of__");
	case 's':
	    return strcmp(s, "setstate__");
	default:
	    return 1;
	}
    }
    return 1;
}

static PyObject *
P_getattr(cPersistentObject *self, PyObject *name)
{
  PyObject *v=NULL;

  char *s;

  PyObject* as_bytes = convert_name(name);
  if (!as_bytes)
    return NULL;

  s = PyBytes_AS_STRING(as_bytes);

  if (s[0] != '_' || unghost_getattr(s))
    {
      if (PER_USE(self))
        {
          v = Py_FindAttr((PyObject*)self, name);
          PER_ALLOW_DEACTIVATION(self);
          PER_ACCESSED(self);
        }
    }
  else
    v = Py_FindAttr((PyObject*)self, name);

  Py_DECREF(as_bytes);

  return v;
}


static PyTypeObject Ptype = {
	PyVarObject_HEAD_INIT(NULL, 0)
	"Persistence.Persistent",     /* tp_name */
  0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
  (getattrofunc)P_getattr,      /* tp_getattro */
  0,                            /* tp_setattro */
  0,                            /* tp_as_buffer */
  Py_TPFLAGS_DEFAULT |
  Py_TPFLAGS_BASETYPE |
  Py_TPFLAGS_HAVE_VERSION_TAG,  /* tp_flags */
	"Persistent ExtensionClass",  /* tp_doc */
};

static struct PyMethodDef _Persistence_methods[] = {
	{NULL,	 (PyCFunction)NULL, 0, NULL}		/* sentinel */
};

#ifdef PY3K
static struct PyModuleDef moduledef =
{
    PyModuleDef_HEAD_INIT,
    "_Persistence",                      /* m_name */
    _Persistence_module_documentation,   /* m_doc */
    -1,                                  /* m_size */
    _Persistence_methods,                /* m_methods */
    NULL,                                /* m_reload */
    NULL,                                /* m_traverse */
    NULL,                                /* m_clear */
    NULL,                                /* m_free */
};
#endif

static PyObject*
module_init(void)
{
  PyObject *m;

  if (! ExtensionClassImported)
    return NULL;

#ifdef PY3K
  cPersistenceCAPI = PyCapsule_Import("persistent.cPersistence.CAPI", 0);
#else
  cPersistenceCAPI = PyCObject_Import("persistent.cPersistence", "CAPI");
#endif
  if (cPersistenceCAPI == NULL)
    return NULL;

  Ptype.tp_bases = Py_BuildValue("OO", cPersistenceCAPI->pertype, ECBaseType);
  if (Ptype.tp_bases == NULL)
    return NULL;
  Ptype.tp_base = cPersistenceCAPI->pertype;
  Ptype.tp_basicsize = cPersistenceCAPI->pertype->tp_basicsize;

  Py_TYPE(&Ptype) = ECExtensionClassType;

  if (PyType_Ready(&Ptype) < 0)
    return NULL;

  /* Create the module and add the functions */
#ifdef PY3K
  m = PyModule_Create(&moduledef);
#else
  m = Py_InitModule3("_Persistence", _Persistence_methods,
                     _Persistence_module_documentation);
#endif

  if (m == NULL)
    return NULL;

  /* Add types: */
  if (PyModule_AddObject(m, "Persistent", (PyObject *)&Ptype) < 0)
    return NULL;

  return m;
}

#ifdef PY3K
PyMODINIT_FUNC PyInit__Persistence(void)
{
    return module_init();
}
#else
PyMODINIT_FUNC init_Persistence(void)
{
    module_init();
}
#endif
