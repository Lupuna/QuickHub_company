#!/bin/sh
# If called very early the curl will receive an "empty" response and a failing status
# As soon as Elasticsearch can process the command, it will return a success status
# as soon as the cluster is yellow or green
seconds=5
until curl 'http://elasticsearch:9200/_cluster/health?wait_for_status=yellow&timeout=30s'; do
  >&2 echo "Elastisearch is unavailable - waiting for it... 😴 ($seconds)"
  sleep 5
  seconds=$(expr $seconds + 5)
done
exec "$@"