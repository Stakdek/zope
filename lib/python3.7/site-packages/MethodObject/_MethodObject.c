/*****************************************************************************

  Copyright (c) 1996-2002 Zope Foundation and Contributors.
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

static PyObject *
of(PyObject *self, PyObject *args)
{
    PyObject *inst;

    if (!PyArg_ParseTuple(args, "O", &inst)) {
        return NULL;
    }

    return PyECMethod_New(self, inst);
}

struct PyMethodDef Method_methods[] = {
  {"__of__",(PyCFunction)of,METH_VARARGS,""},  
  {NULL,		NULL}		/* sentinel */
};

static struct PyMethodDef methods[] = {{NULL,	NULL}};

#ifdef PY3K
static struct PyModuleDef moduledef =
{
    PyModuleDef_HEAD_INIT,
    "_MethodObject",                            /* m_name */
    "Method-object mix-in class module\n\n",    /* m_doc */
    -1,                                         /* m_size */
    methods,                                    /* m_methods */
    NULL,                                       /* m_reload */
    NULL,                                       /* m_traverse */
    NULL,                                       /* m_clear */
    NULL,                                       /* m_free */
};
#endif


static PyObject*
module_init(void)
{
  PyObject *m, *d;
  PURE_MIXIN_CLASS(Method,
	"Base class for objects that want to be treated as methods\n"
	"\n"
	"The method class provides a method, __of__, that\n"
	"binds an object to an instance.  If a method is a subobject\n"
	"of an extension-class instance, the the method will be bound\n"
	"to the instance and when the resulting object is called, it\n"
	"will call the method and pass the instance in addition to\n"
	"other arguments.  It is the responsibility of Method objects\n"
	"to implement (or inherit) a __call__ method.\n",
	Method_methods);

#ifdef PY3K
  m = PyModule_Create(&moduledef);
#else
  m = Py_InitModule3(
        "_MethodObject",
        methods,
		"Method-object mix-in class module\n\n");
#endif

  if (m == NULL) {
      return NULL;
  }

  d = PyModule_GetDict(m);
  if (d == NULL) {
      return NULL;
  }

  PyExtensionClass_Export(d, "Method", MethodType);

  return m;
}

#ifdef PY3K
PyMODINIT_FUNC PyInit__MethodObject(void)
{
    return module_init();
}
#else
PyMODINIT_FUNC init_MethodObject(void)
{
    module_init();
}
#endif
