#!/bin/bash
# Script to run tests with proper environment configuration

PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python -m pytest "$@"

