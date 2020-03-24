from importlib import import_module


def import_provider_class(provider):
    app_path = '.'.join(__name__.split('.')[:-1])
    adapter_path = f"{app_path}.adapters.{provider}"
    module = import_module(adapter_path)
    return module.Adapter
