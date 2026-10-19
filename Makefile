.PHONY: install run test clean
install:
	python3 -m pip install -r requirements.txt
run:
	python3 app.py
test:
	python3 -m unittest discover -s tests -v
clean:
	rm -rf __pycache__ src/__pycache__ tests/__pycache__
