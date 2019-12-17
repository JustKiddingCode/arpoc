# import all modules in this directory,
# from user ted @ https://stackoverflow.com/a/59054776
from importlib import import_module
from pathlib import Path

__all__ = [
        import_module(f".{f.stem}", __package__)
        for f in Path(__file__).parent.glob("*.py")
        if "__" not in f.stem
]
