.PHONY: install run test clean

install:
	pip install -r requirements.txt

run:
	streamlit run app/main.py

test:
	python -m pytest tests/ -v

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
