import nox
from pathlib import Path

ROOT = Path(".")
PYTHON_VERSIONS = ["3.11"]
PYTHON_DEFAULT_VERSION = PYTHON_VERSIONS[-1]

nox.options.stop_on_first_error = True
nox.options.reuse_existing_virtualenvs = True


@nox.session(python=PYTHON_DEFAULT_VERSION)
def test(session: nox.Session):
    session.run("poetry", "install", external=True)
    session.run("pytest")
    # list files in notebooks directory
    files = list(ROOT.glob("notebooks/*.ipynb"))
    for file in files:
        session.run("pytest", "--nbval-lax", file)
