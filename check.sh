#!/usr/bin/env bash

# Get path from argument or use current directory as default
path=${1:-.}

# Run checks and store exit statuses
printf "Running checks...\n"
printf "Black...\n"
black --check $path || black_status=$?
printf "\nMypy...\n"
mypy $path || mypy_status=$?
printf "\nRuff...\n"
ruff check $path || ruff_status=$?


# Print summary
printf "\nSummary of check results:\n"
printf "Black:\t${black_status:-OK}\n"
printf "Mypy:\t${mypy_status:-OK}\n"
printf "Ruff:\t${ruff_status:-OK}\n"

# Exit with 1 if any check failed
if [ -n "$black_status" ] || [ -n "$mypy_status" ] || [ -n "$ruff_status" ] || [ -n "$isort_status" ]; then
  exit 1
fi
