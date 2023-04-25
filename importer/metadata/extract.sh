#!/bin/bash

# Extract flight frame data from .mp4 recording
docker run --name flightparser -v "$1":/home/pdraw/raw --rm flightparser:latest vmeta-extract --pretty --json "/home/pdraw/raw/$2.json" "/home/pdraw/raw/$2"