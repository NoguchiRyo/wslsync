#!/bin/bash
# Test backup script

echo "Starting backup process..."
rsync -av /source/ /destination/
echo "Backup completed!"