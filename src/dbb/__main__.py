""" Main application entry point.

    python -m DataBookBinder  ...

"""

from .util import config
from .util import log
from .databook import DataBook


def main():
    db = DataBook()
    db.compile()
    db.link()


if __name__ == "__main__":
    log.info("Databook generator")
    raise SystemExit(main())
