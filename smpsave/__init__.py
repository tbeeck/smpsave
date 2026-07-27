from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("smpsave")
except PackageNotFoundError:
    # Running from a source tree without the package installed.
    __version__ = "0.0.0+unknown"
