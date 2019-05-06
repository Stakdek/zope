/*****************************************************************************

  Copyright (c) 1996-2003 Zope Foundation and Contributors.
  All Rights Reserved.

  This software is subject to the provisions of the Zope Public License,
  Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
  THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
  WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
  WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
  FOR A PARTICULAR PURPOSE

 ****************************************************************************/
#include "ExtensionClass/ExtensionClass.h"
#include "ExtensionClass/_compat.h"

#define UNLESS(E) if(!(E))
#define OBJECT(O) ((PyObject*)(O))

typedef struct {
  PyObject_HEAD
  PyObject *callable;
  int level;
} CA;

static PyObject *
CA__init__(CA *self, PyObject *args)
{
  PyObject *callable;
  int level=0;

  UNLESS(PyArg_ParseTuple(args,"O|i",&callable, &level)) return NULL;

  if (level > 0) 
    {
      callable=PyObject_CallFunction(OBJECT(Py_TYPE(self)), "Oi", 
				     callable, level-1);
      UNLESS (callable) return NULL;
      self->level=level;
    }
  else
    {
      Py_INCREF(callable);
      self->level=0;
    }

  self->callable=callable;

  Py_INCREF(Py_None);
  return Py_None;
}

static void
CA_dealloc(CA *self)     
{
  Py_DECREF(self->callable);
  Py_DECREF(Py_TYPE(self));
  Py_TYPE(self)->tp_free(OBJECT(self));
}

static PyObject *
CA_of(CA *self, PyObject *args)
{
  if (self->level > 0) 
    {
      Py_INCREF(self->callable);
      return self->callable;
    }

  if (NATIVE_CHECK(self->callable))
    {
      /* Special case string as simple alias. */
      PyObject *o;

      UNLESS (PyArg_ParseTuple(args,"O", &o)) return NULL;
      return PyObject_GetAttr(o, self->callable);
    }

  return PyObject_CallObject(self->callable, args);
}

static struct PyMethodDef CA_methods[] = {
  {"__init__",(PyCFunction)CA__init__, METH_VARARGS, ""},
  {"__of__",  (PyCFunction)CA_of,      METH_VARARGS, ""},
  {NULL,		NULL}		/* sentinel */
};

static PyExtensionClass ComputedAttributeType = {
  PyVarObject_HEAD_INIT(NULL, 0)
  "ComputedAttribute", sizeof(CA),
  0,
  (destructor)CA_dealloc,
  0,0,0,0,0,   0,0,0,   0,0,0,0,0,   0,0,
  "ComputedAttribute(callable) -- Create a computed attribute",
  METHOD_CHAIN(CA_methods), 
  (void*)(EXTENSIONCLASS_BINDABLE_FLAG)
};

static struct PyMethodDef methods[] = {
  {NULL,		NULL}
};

#ifdef PY3K
static struct PyModuleDef moduledef =
{
    PyModuleDef_HEAD_INIT,
    "_ComputedAttribute",                   /* m_name */
    "Provide ComputedAttribute\n\n",        /* m_doc */
    -1,                                     /* m_size */
    methods,                                /* m_methods */
    NULL,                                   /* m_reload */
    NULL,                                   /* m_traverse */
    NULL,                                   /* m_clear */
    NULL,                                   /* m_free */
};
#endif


static PyObject*
module_init(void)
{
  PyObject *m, *d;

  UNLESS(ExtensionClassImported) return NULL;
  
#ifdef PY3K
  m = PyModule_Create(&moduledef);
#else
  m = Py_InitModule3(
        "_ComputedAttribute",
        methods,
        "Provide Computed Attributes\n\n");
#endif

  if (m == NULL) {
      return NULL;
  }

  d = PyModule_GetDict(m);
  if (d == NULL) {
      return NULL;
  }

  PyExtensionClass_Export(d, "ComputedAttribute", ComputedAttributeType);

  return m;
}

#ifdef PY3K
PyMODINIT_FUNC PyInit__ComputedAttribute(void)
{
    return module_init();
}
#else
PyMODINIT_FUNC init_ComputedAttribute(void)
{
    module_init();
}
#endif
