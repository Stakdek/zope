##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
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
"""Source widgets support
"""
import xml.sax.saxutils

from zope.component import adapter, getMultiAdapter
from zope.interface import implementer
import zope.browser.interfaces
import zope.schema.interfaces
from zope.schema.interfaces import \
    ISourceQueriables, ValidationError, IVocabularyTokenized, IIterableSource

import zope.formlib.interfaces
import zope.formlib.widget
import zope.formlib.itemswidgets
from zope.formlib._compat import imap
from zope.formlib.interfaces import (
    WidgetInputError,
    MissingInputError,
    ISourceQueryView,
    IWidgetInputErrorView,
    IDisplayWidget,
    IInputWidget)
from zope.formlib.i18n import _
from zope.formlib.widgets import (
    SelectWidget, RadioWidget, MultiSelectWidget, OrderedMultiSelectWidget,
    MultiCheckBoxWidget, MultiSelectSetWidget, MultiSelectFrozenSetWidget)
from zope.formlib.widget import DisplayWidget, InputWidget
from zope.formlib._compat import safeBase64Encode

@implementer(IDisplayWidget)
class SourceDisplayWidget(DisplayWidget):

    def __init__(self, field, source, request):
        super(SourceDisplayWidget, self).__init__(field, request)
        self.source = source

    required = False

    def hidden(self):
        return ''

    def error(self):
        return ''

    def __call__(self):
        """Render the current value
        """

        if self._renderedValueSet():
            value = self._data
        else:
            value = self.context.default

        if value == self.context.missing_value:
            value = self._translate(_("SourceDisplayWidget-missing",
                                      default="Nothing"))
        else:
            terms = getMultiAdapter((self.source, self.request),
                zope.browser.interfaces.ITerms)

            try:
                term = terms.getTerm(value)
            except LookupError:
                value = self._translate(_("SourceDisplayWidget-invalid",
                                          default="Invalid value"))
            else:
                value = self.renderTermForDisplay(term)

        return value

    def renderTermForDisplay(self, term):
        # Provide a rendering of `term` for display; this is not for
        # use when generating a select list.
        return xml.sax.saxutils.escape(self._translate(term.title))


class SourceSequenceDisplayWidget(SourceDisplayWidget):

    separator = '<br />\n'

    def __call__(self):

        if self._renderedValueSet():
            seq = self._data
        else:
            seq = self.context.default

        terms = getMultiAdapter((self.source, self.request),
            zope.browser.interfaces.ITerms)
        result = []
        for value in seq:
            try:
                term = terms.getTerm(value)
            except LookupError:
                value = self._translate(_("SourceDisplayWidget-invalid",
                                          default="Invalid value"))
            else:
                value = self.renderTermForDisplay(term)

            result.append(value)

        return self.separator.join(result)


@implementer(IInputWidget)
class SourceInputWidget(InputWidget):

    _error = None


    def __init__(self, field, source, request):
        super(SourceInputWidget, self).__init__(field, request)
        self.source = source
        self.terms = getMultiAdapter((source, self.request),
            zope.browser.interfaces.ITerms)

    def queryviews(self):
        queriables = ISourceQueriables(self.source, None)
        if queriables is None:
            # treat the source itself as a queriable
            queriables = ((self.name + '.query', self.source), )
        else:
            queriables = [
                (self.name + '.' + safeBase64Encode(i), s)
                          for (i, s) in queriables.getQueriables()]

        return [
            (name, getMultiAdapter(
                    (source, self.request),
                    ISourceQueryView,
                    )
             ) for (name, source) in queriables]

    queryviews = property(queryviews)

    def _value(self):
        if self._renderedValueSet():
            value = self._data
        else:
            for name, queryview in self.queryviews:
                if name+'.apply' in self.request:
                    token = self.request.form.get(name+'.selection')
                    if token is not None:
                        break
                else:
                    token = self.request.form.get(self.name)

            if token is not None:
                try:
                    value = self.terms.getValue(str(token))
                except LookupError:
                    value = self.context.missing_value
            else:
                value = self.context.missing_value

        return value

    def hidden(self):
        value = self._value()
        if value == self.context.missing_value:
            return '' # Nothing to hide ;)

        try:
            term = self.terms.getTerm(value)
        except LookupError:
            # A value was set, but it's not valid.  Treat
            # it as if it was missing and return nothing.
            return ''

        return ('<input type="hidden" name="%s" value=%s />'
                % (self.name, xml.sax.saxutils.quoteattr(term.token))
                )

    def error(self):
        if self._error:
            # TODO This code path is untested.
            return getMultiAdapter((self._error, self.request),
                                   IWidgetInputErrorView).snippet()
        return ""

    def __call__(self):
        result = ['<div class="value">']
        value = self._value()
        field = self.context

        term = None
        if value == field.missing_value:
            result.append('  <div class="row">')
            result.append('    <div class="label">')
            result.append(u'     ' +
                          self._translate(_("SourceDisplayWidget-label",
                                            default="Selected"))
                          )
            result.append('    </div>')
            result.append('    <div class="field">')
            result.append(u'     ' +
                          self._translate(_("SourceDisplayWidget-missing",
                                            default="Nothing"))
                          )
            result.append('    </div>')
            result.append('  </div>')
        else:
            try:
                term = self.terms.getTerm(value)
            except LookupError:
                result.append(u'  ' +
                              self._translate(_("SourceDisplayWidget-missing",
                                                default="Nothing Valid"))
                              )
            else:
                result.append('  <div class="row">')
                result.append('    <div class="label">')
                result.append(u'     ' +
                              self._translate(_("SourceDisplayWidget-label",
                                                default="Selected"))
                              )
                result.append('    </div>')
                result.append('    <div class="field">')
                result.append(u'     ' + self.renderTermForDisplay(term))
                result.append('    </div>')
                result.append('  </div>')
                result.append(
                    '  <input type="hidden" name="%s" value=%s />'
                    % (self.name, xml.sax.saxutils.quoteattr(term.token)))

        result.append('  <input type="hidden" name="%s.displayed" value="y" />'
                      % self.name)

        result.append('  <div class="queries">')
        for name, queryview in self.queryviews:
            result.append('    <div class="query">')
            result.append('      <div class="queryinput">')
            result.append(queryview.render(name))
            result.append('      </div> <!-- queryinput -->')

            qresults = queryview.results(name)
            if qresults:
                result.append('      <div class="queryresults">\n%s' %
                              self._renderResults(qresults, name))
                result.append('      </div> <!-- queryresults -->')
            result.append('    </div> <!-- query -->')
        result.append('  </div> <!-- queries -->')
        result.append('</div> <!-- value -->')
        return '\n'.join(result)

    def _renderResults(self, results, name):
        terms = []
        for value in results:
            term = self.terms.getTerm(value)
            terms.append((self._translate(term.title), term.token))
        terms.sort()

        apply = self._translate(_("SourceInputWidget-apply", default="Apply"))
        return (
            '<select name="%s.selection">\n'
            '%s\n'
            '</select>\n'
            '<input type="submit" name="%s.apply" value="%s" />'
            % (name,
               '\n'.join(
                   [('<option value="%s">%s</option>'
                     % (token, title))
                    for (title, token) in terms]),
               name,
               apply)
            )

    def renderTermForDisplay(self, term):
        # Provide a rendering of `term` for display; this is not for
        # use when generating a select list.
        return xml.sax.saxutils.escape(self._translate(term.title))

    required = property(lambda self: self.context.required)

    def getInputValue(self):
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                token = self.request.form.get(name+'.selection')
                if token is not None:
                    break
        else:
            token = self.request.get(self.name)

        field = self.context

        if token is None:
            if field.required:
                # TODO This code path is untested.
                raise MissingInputError(
                    field.__name__, self.label,
                    )
            return field.missing_value

        try:
            value = self.terms.getValue(str(token))
        except LookupError:
            # TODO This code path is untested.
            err = zope.schema.interfaces.ValidationError(
                "Invalid value id", token)
            raise WidgetInputError(field.__name__, self.label, err)

        # Remaining code copied from SimpleInputWidget

        # value must be valid per the field constraints
        try:
            field.validate(value)
        except ValidationError as err:
            # TODO This code path is untested.
            self._error = WidgetInputError(field.__name__, self.label, err)
            raise self._error

        return value

    def hasInput(self):
        if self.name in self.request or self.name+'.displayed' in self.request:
            return True

        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                token = self.request.form.get(name+'.selection')
                if token is not None:
                    return True

        return False

class SourceListInputWidget(SourceInputWidget):

    def _input_value(self):
        tokens = self.request.form.get(self.name)
        for name, queryview in self.queryviews:
            if name+'.apply' in self.request:
                newtokens = self.request.form.get(name+'.selection')
                if newtokens:
                    if tokens:
                        tokens = tokens + newtokens
                    else:
                        tokens = newtokens

        if tokens:
            remove = self.request.form.get(self.name+'.checked')
            if remove and (self.name+'.remove' in self.request):
                tokens = [token
                          for token in tokens
                          if token not in remove
                          ]
            value = []
            for token in tokens:
                try:
                    v = self.terms.getValue(str(token))
                except LookupError:
                    pass # skip invalid tokens (shrug)
                else:
                    value.append(v)
        else:
            if self.name+'.displayed' in self.request:
                value = []
            else:
                value = self.context.missing_value

        if value:
            r = []
            seen = {}
            for s in value:
                if s not in seen:
                    r.append(s)
                    seen[s] = 1
            value = r

        return value

    def _value(self):
        if self._renderedValueSet():
            value = self._data
        else:
            value = self._input_value()

        return value

    def hidden(self):
        value = self._value()
        if value == self.context.missing_value:
            return '' # Nothing to hide ;)

        result = []
        for v in value:
            try:
                term = self.terms.getTerm(value)
            except LookupError:
                # A value was set, but it's not valid.  Treat
                # it as if it was missing and skip
                continue
            else:
                result.append(
                    '<input type="hidden" name="%s:list" value=%s />'
                    % (self.name, xml.sax.saxutils.quoteattr(term.token))
                    )

    def __call__(self):
        result = ['<div class="value">']
        value = self._value()

        if value:
            for v in value:
                try:
                    term = self.terms.getTerm(v)
                except LookupError:
                    continue # skip
                else:
                    result.append(
                        '  <input type="checkbox" name="%s.checked:list"'
                        ' value=%s />'
                        % (self.name, xml.sax.saxutils.quoteattr(term.token))
                        )
                    result.append('  ' + self.renderTermForDisplay(term))
                    result.append(
                        '  <input type="hidden" name="%s:list" value=%s />'
                        % (self.name, xml.sax.saxutils.quoteattr(term.token)))
                    result.append('  <br />')

            result.append(
                '  <input type="submit" name="%s.remove" value="%s" />'
                % (self.name,
                   self._translate(_("MultipleSourceInputWidget-remove",
                                     default="Remove")))
                )
            result.append('  <br />')

        result.append('  <input type="hidden" name="%s.displayed" value="y" />'
                      % self.name)

        result.append('  <div class="queries">')

        for name, queryview in self.queryviews:
            result.append('    <div class="query">')
            result.append('      <div class="queryinput">')
            result.append(queryview.render(name))
            result.append('      </div> <!-- queryinput -->')

            qresults = queryview.results(name)
            if qresults:
                result.append('      <div class="queryresults">\n%s' %
                              self._renderResults(qresults, name))
                result.append('      </div> <!-- queryresults -->')
            result.append('    </div> <!-- query -->')

        result.append('  </div> <!-- queries -->')
        result.append('</div> <!-- value -->')
        return '\n'.join(result)

    def _renderResults(self, results, name):
        terms = []
        apply = self._translate(_("SourceListInputWidget-apply",
                                  default="Apply"))
        for value in results:
            term = self.terms.getTerm(value)
            terms.append((self._translate(term.title), term.token))
        terms.sort()
        return (
            '<select name="%s.selection:list" multiple>\n'
            '%s\n'
            '</select>\n'
            '<input type="submit" name="%s.apply" value="%s" />'
            % (name,
               '\n'.join([('<option value="%s">%s</option>' % (token, title))
                          for (title, token) in terms]),
               name,
               apply)
            )

    def getInputValue(self):
        value = self._input_value()

        # Remaining code copied from SimpleInputWidget

        # value must be valid per the field constraints
        field = self.context
        try:
            field.validate(value)
        except ValidationError as err:
            # TODO This code path is untested.
            self._error = WidgetInputError(field.__name__, self.label, err)
            raise self._error

        return value

    def hasInput(self):
        return self.name+'.displayed' in self.request.form


# Input widgets for IIterableSource:

# These widgets reuse the old-style vocabulary widgets via the class
# IterableSourceVocabulary that adapts a source (and its ITerms object)
# into a vocabulary. When/if vocabularies go away, these classes
# should be updated into full implementations.


@implementer(IVocabularyTokenized)
@adapter(IIterableSource)
class IterableSourceVocabulary(object):

    """Adapts an iterable source into a legacy vocabulary.

    This can be used to wrap sources to make them usable with widgets that
    expect vocabularies. Note that there must be an ITerms implementation
    registered to obtain the terms.
    """

    def __init__(self, source, request):
        self.source = source
        self.terms = getMultiAdapter((source, request),
            zope.browser.interfaces.ITerms)

    def getTerm(self, value):
        return self.terms.getTerm(value)

    def getTermByToken(self, token):
        value = self.terms.getValue(token)
        return self.getTerm(value)

    def __iter__(self):
        return imap(
            lambda value: self.getTerm(value), self.source.__iter__())

    def __len__(self):
        return self.source.__len__()

    def __contains__(self, value):
        return self.source.__contains__(value)


class SourceSelectWidget(SelectWidget):
    """Provide a selection list for the item."""

    def __init__(self, field, source, request):
        super(SourceSelectWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)
        # BBB
        if not zope.formlib.itemswidgets.EXPLICIT_EMPTY_SELECTION:
            # Even if the field is required, no input is needed, so don't
            # worry the user about it:
            self.required = False

class SourceDropdownWidget(SourceSelectWidget):
    """Variation of the SourceSelectWidget that uses a drop-down list."""

    size = 1
    explicit_empty_selection = True

class SourceRadioWidget(RadioWidget):
    """Radio widget for single item choices."""

    def __init__(self, field, source, request):
        super(SourceRadioWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)

class SourceMultiSelectWidget(MultiSelectWidget):
    """A multi-selection widget with ordering support."""

    def __init__(self, field, source, request):
        super(SourceMultiSelectWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)

class SourceOrderedMultiSelectWidget(OrderedMultiSelectWidget):
    """A multi-selection widget with ordering support."""

    def __init__(self, field, source, request):
        super(SourceOrderedMultiSelectWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)

class SourceMultiSelectSetWidget(MultiSelectSetWidget):
    """Provide a selection list for the set to be selected."""

    def __init__(self, field, source, request):
        super(SourceMultiSelectSetWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)

class SourceMultiSelectFrozenSetWidget(MultiSelectFrozenSetWidget):
    """Provide a selection list for the frozenset to be selected."""

    def __init__(self, field, source, request):
        super(SourceMultiSelectFrozenSetWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)

class SourceMultiCheckBoxWidget(MultiCheckBoxWidget):
    """Provide a list of checkboxes that provide the choice for the list."""

    def __init__(self, field, source, request):
        super(SourceMultiCheckBoxWidget, self).__init__(
            field, IterableSourceVocabulary(source, request), request)
