import multiprocessing

bind = "0.0.0.0:5002"
workers = 8
threads = 8
worker_class = "gthread"
timeout = 120
keepalive = 65
max_requests = 10000
max_requests_jitter = 1000

accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
