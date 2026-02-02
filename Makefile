.PHONY: setup lint test

setup:
\tpython -m pip install --upgrade pip
\tpip install -r requirements.txt

lint:
\truff check .

test:
\tpytest -q
