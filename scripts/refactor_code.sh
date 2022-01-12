#!/bin/bash
find . -type f -name "*.py" | xargs autoflake --in-place --remove-all-unused-imports
find . -type f -name "*.py" | xargs isort
