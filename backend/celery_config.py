from celery import Celery

# We define the Redis broker URL. 
# 'redis://redis:6379/0' uses the 'redis' service name 
# from our docker-compose.yml
BROKER_URL = 'redis://redis:6379/0'
RESULT_BACKEND = 'redis://redis:6379/0'

# Create the Celery app instance
celery_app = Celery(
    'worker',
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
    include=['worker']  # Tells Celery to look for tasks in 'worker.py'
)

celery_app.conf.update(
    task_track_started=True,
)