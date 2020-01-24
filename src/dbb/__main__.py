""" Main application entry point.

    python -m DataBookBinder2  ...

"""

from . import cli
from .databook import DataBook

# def main():
#     """ Execute the application.

#     """
#     cli.main()


def main():
    db = DataBook()
    db.compile()
    db.link()


if __name__ == "__main__":
    log.info("Databook generator")

    main()




# Make the script executable.

if __name__ == "__main__":
    raise SystemExit(main())
