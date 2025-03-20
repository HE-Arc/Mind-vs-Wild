import json
import random
import aiohttp
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from mindvswild.models import GroupUser  


