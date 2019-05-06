##############################################################################
#
# Copyright (c) 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Interface that describes the 'macros' attribute of a PageTemplate.
"""
from zope.interface import Interface, Attribute


class IPageTemplate(Interface):
    """Objects that can render page templates
    """

    def __call__(*args, **kw):
        """Render a page template

        The argument handling is specific to particular
        implementations.  Normally, however, positional arguments are
        bound to the top-level ``args`` variable and keyword arguments
        are bound to the top-level ``options`` variable.
        """

    def pt_edit(source, content_type):
        """Set the source and content type
        """

    def pt_errors(namespace):
        """Return a sequence of strings that describe errors in the template.

        The errors may occur when the template is compiled or
        rendered.

        *namespace* is the set of names passed to the TALES expression
        evaluator, similar to what's returned by pt_getContext().

        This can be used to let a template author know what went wrong
        when an attempt was made to render the template.
        """

    def read():
        """Get the template source
        """

    macros = Attribute("An object that implements the ``__getitem__`` "
                       "protocol (e.g., a :class:`dict`), containing page template macros.")

class IPageTemplateSubclassing(IPageTemplate):
    """Behavior that may be overridden or used by subclasses
    """


    def pt_getContext(**kw):
        """Compute a dictionary of top-level template names

        Responsible for returning the set of
        top-level names supported in path expressions

        """

    def pt_getEngine():
        """Returns the TALES expression evaluator.
        """

    def pt_getEngineContext(namespace):
        """Return an execution context from the expression engine."""

    def __call__(*args, **kw):
        """Render a page template

        This is sometimes overridden to provide additional argument
        binding.
        """

    def pt_source_file():
        """return some text describing where a bit of ZPT code came from.

        This could be a file path, a object path, etc.
        """

    def _cook():
        """Compile the source

        Results are saved in the variables: ``_v_errors``, ``_v_warnings``,
        ``_v_program``, and ``_v_macros``, and the flag ``_v_cooked`` is set.
        """
    def _cook_check():
        """Compiles the source if necessary

        Subclasses might override this to influence the decision about
        whether compilation is necessary.
        """

    content_type = Attribute("The content-type of the generated output")

    expand = Attribute(
        "Flag indicating whether the read method should expand macros")


class IPageTemplateEngine(Interface):
    """Template engine implementation.

    The engine must provide a ``cook`` method to return a cooked
    template program from a source input.
    """

    def cook(source_file, text, engine, content_type):
        """Parse text and return prepared template program and macros.

        Note that while *source_file* is provided to name the source
        of the input *text*, it should not be relied on to be an
        actual filename (it may be an application-specific, virtual
        path).

        The return type is a tuple ``(program, macros)``.
        """


class IPageTemplateProgram(Interface):
    """Cooked template program."""

    def __call__(
            context, macros, debug=0, wrap=60, metal=1, tal=1, showtal=-1,
            strictinsert=1, stackLimit=100, i18nInterpolate=1,
            sourceAnnotations=0):
        """
        Render template in the provided template *context*.

        Optional arguments:

        :keyword bool debug: enable debugging output to sys.stderr (off by default).
        :keyword int wrap: try to wrap attributes on opening tags to this number of
            column (default: 60).
        :keyword bool metal: enable METAL macro processing (on by default).
        :keyword bool tal: enable TAL processing (on by default).
        :keyword int showtal: do not strip away TAL directives.  A special value of
            -1 (which is the default setting) enables showtal when TAL
            processing is disabled, and disables showtal when TAL processing is
            enabled.  Note that you must use 0, 1, or -1; true boolean values
            are not supported (for historical reasons).
        :keyword bool strictinsert: enable TAL processing and stricter HTML/XML
            checking on text produced by structure inserts (on by default).
            Note that Zope turns this value off by default.
        :keyword int stackLimit: set macro nesting limit (default: 100).
        :keyword bool i18nInterpolate: enable i18n translations (default: on).
        :keyword bool sourceAnnotations: enable source annotations with HTML comments
            (default: off).
        """
