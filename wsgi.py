import importlib.util, os
spec = importlib.util.spec_from_file_location("application", os.path.join(os.path.dirname(__file__), "app.py"))
mod = importlib.util.load_from_spec(spec)
spec.loader.exec_module(mod)
app = mod.app
