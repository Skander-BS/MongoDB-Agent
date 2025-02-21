ifeq ($(OS),Windows_NT)
    PYTHON = python
    PYTHON_VENV = $(VENV)\Scripts\python.exe
    SET_PYTHONPATH = set PYTHONPATH=src &&
    BG =
else
    PYTHON = python3
    PYTHON_VENV = $(VENV)/bin/python
    SET_PYTHONPATH = PYTHONPATH=src
    BG = &
endif

VENV ?= venv
UVICORN_HOST ?= 127.0.0.1
UVICORN_PORT ?= 8000
STREAMLIT_PORT ?= 8501

.PHONY: init start stop

init:
	@echo "Creating virtual environment and installing dependencies..."
	$(PYTHON) -m venv $(VENV)
	$(PYTHON_VENV) -m pip install --upgrade pip
	$(PYTHON_VENV) -m pip install -r requirements.txt

start:
	@echo "Starting uvicorn and streamlit..."
	# Start uvicorn with PYTHONPATH set appropriately.
	$(SET_PYTHONPATH) $(PYTHON_VENV) -m uvicorn src.api.main:app --port $(UVICORN_PORT) --reload $(BG)
	$(PYTHON_VENV) -m streamlit run src/app/main.py --server.port $(STREAMLIT_PORT)

stop:
	@echo "Stopping uvicorn and streamlit..."
ifeq ($(OS),Windows_NT)
	@taskkill /F /IM uvicorn.exe || exit 0
	@taskkill /F /IM streamlit.exe || exit 0
else
	@pkill -f "uvicorn src.api.main:app" || true
	@pkill -f "streamlit run src/app/main.py" || true
endif