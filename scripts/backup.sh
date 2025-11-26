#!/bin/bash
# ${NAME_OF_APPLICATION} Backup Script

BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/ai_haccp_backup_$DATE"

mkdir -p "$BACKUP_DIR"

echo "Creating backup: $BACKUP_FILE"
PORT=$((PORT_RANGE_BEGIN + USER_ID * RANGE_RESERVED)) HTTPS_PORT=$((PORT_RANGE_BEGIN + USER_ID * RANGE_RESERVED + 1)) USER_ID=$USER_ID docker-compose -f docker-compose.prod.yml exec -T api cp /app/data/ai_haccp.db /tmp/backup.db
docker cp $(docker-compose -f docker-compose.prod.yml ps -q api):/tmp/backup.db "$BACKUP_FILE.db"

if [[ $? -eq 0 ]]; then
    echo "Backup created successfully: $BACKUP_FILE"
    
    # Keep only last 7 backups
    ls -t "$BACKUP_DIR"/ai_haccp_backup_*.db | tail -n +8 | xargs -r rm
    echo "Old backups cleaned up"
else
    echo "Backup failed!"
    exit 1
fi
