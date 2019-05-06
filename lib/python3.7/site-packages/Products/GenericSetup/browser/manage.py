from Products.Five import BrowserView
from Products.GenericSetup.registry import _import_step_registry
from Products.GenericSetup.registry import _export_step_registry


class ImportStepsView(BrowserView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.global_registry = _import_step_registry
        self.tool_registry = context.getImportStepRegistry()

    def invalidSteps(self):
        steps = self.tool_registry.listStepMetadata()
        steps = [step for step in steps if step['invalid']]
        return steps

    def doubleSteps(self):
        steps = set(self.tool_registry.listSteps())
        globals = set(self.global_registry.listSteps())
        steps = steps.intersection(globals)
        steps = [self.tool_registry.getStepMetadata(step) for step in steps]
        steps.sort()
        return steps


class ExportStepsView(ImportStepsView):
    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.global_registry = _export_step_registry
        self.tool_registry = context.getExportStepRegistry()
