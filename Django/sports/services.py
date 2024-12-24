import redis
import json
from .models import Moneyline
import logging

logger = logging.getLogger("logsport")

# Connect to Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

def get_chart_data(game_id):
    # Define Redis cache key
    cache_key = f"chart_data_game_{game_id}"

    # Check if data is in Redis
    data = r.get(cache_key)
    if data:
        logger.info(f"Cache hit for game_id: {game_id}")
        return json.loads(data)  # Deserialize the JSON data

    # If not in cache, fetch from database
    logger.info(f"Cache miss for game_id: {game_id}. Fetching from database.")
    data = Moneyline.objects.filter(game=game_id).order_by("event_timestamp")
    
    # Serialize the data
    serialized_data = [{"timestamp": d.event_timestamp, "line": d.line_1} for d in data]
    
    # Cache the data in Redis for 2 hours (7200 seconds)
    r.setex(cache_key, 7200, json.dumps(serialized_data))
    logger.info(f"Data cached for game_id: {game_id}")

    return serialized_data
