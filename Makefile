PROJECT := car
SRC := src/main.py
BIN_DIR := bin

all: build

deps:
	@echo "==> Installing Python dependencies..."
	pip install -r requirements.txt --break-system-packages
	pip install nuitka --break-system-packages

build: deps
	@echo "==> Building $(PROJECT) with..."
	mkdir -p $(BIN_DIR)
	nuitka --onefile --output-dir=$(BIN_DIR) $(SRC)
	@echo "==> Build complete → $(BIN_DIR)/$(PROJECT)"

clean:
	@echo "==> Cleaning..."
	rm -rf $(BIN_DIR)
	rm -rf *.build *.dist *.onefile-build
	@echo "==> Clean done."

.PHONY: all deps build run clean
