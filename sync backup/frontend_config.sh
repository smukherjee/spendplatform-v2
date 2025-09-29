#!/bin/bash

# Frontend Configuration Wrapper Script
# Provides easy access to frontend configuration management

cd "$(dirname "${BASH_SOURCE[0]}")" || exit 1
node frontend_config.cjs "$@"