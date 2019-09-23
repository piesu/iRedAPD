#!/usr/bin/env python

# Author: Zhang Huangbin <zhb@iredmail.org>
# Purpose: Cleanup expired throttle and greylisting tracking records.

import os
import sys
import time
import web

os.environ['LC_ALL'] = 'C'

rootdir = os.path.abspath(os.path.dirname(__file__)) + '/../'
sys.path.insert(0, rootdir)

import settings
from tools import logger, get_db_conn, sql_count_id

web.config.debug = False

backend = settings.backend
logger.info('* Backend: %s' % backend)

now = int(time.time())

conn_iredapd = get_db_conn('iredapd')

#
# Throttling
#
total_before = sql_count_id(conn_iredapd, 'throttle_tracking')
conn_iredapd.delete('throttle_tracking', where='init_time + period < %d' % now)
total_after = sql_count_id(conn_iredapd, 'throttle_tracking')

logger.info("* Remove expired throttle tracking records: "
            "%d removed, %d left." % (total_before - total_after, total_after))

#
# Greylisting tracking records.
#
total_before = sql_count_id(conn_iredapd, 'greylisting_tracking')
conn_iredapd.delete('greylisting_tracking', where='record_expired < %d' % now)
total_after = sql_count_id(conn_iredapd, 'greylisting_tracking')

#
# Some basic analyzation
#
# Count how many records are passed greylisting
total_passed = sql_count_id(conn_iredapd, 'greylisting_tracking', where='passed=1')

logger.info("* Remove expired greylisting tracking records: "
            "%d removed, %d left (%d passed, %d not)." % (
                total_before - total_after,
                total_after,
                total_passed,
                total_after - total_passed))

#
# Clean up cached senderscore results.
#
expire_seconds = int(time.time()) - (settings.SENDERSCORE_CACHE_DAYS * 86400)
total_before = sql_count_id(conn_iredapd, 'senderscore_cache')
conn_iredapd.delete('senderscore_cache', where='time < %d' % expire_seconds)
total_after = sql_count_id(conn_iredapd, 'senderscore_cache')

logger.info("* Remove expired senderscore DNS query results: "
            "%d removed, %d left." % (total_before - total_after, total_after))

#
# Clean up `log_smtp_actions`
#
expire_seconds = int(time.time()) - (settings.LOG_SMTP_ACTIONS_EXPIRE_DAYS * 86400)
total_before = sql_count_id(conn_iredapd, 'log_smtp_actions')
conn_iredapd.delete('senderscore_cache', where='time < %d' % expire_seconds)
total_after = sql_count_id(conn_iredapd, 'log_smtp_actions')

logger.info("* Remove expired smtp action log: "
            "%d removed, %d left." % (total_before - total_after, total_after))

#
# Clean up `log_smtp_auth`
#
expire_seconds = int(time.time()) - (settings.LOG_SMTP_AUTH_EXPIRE_DAYS * 86400)
total_before = sql_count_id(conn_iredapd, 'log_smtp_auth')
conn_iredapd.delete('senderscore_cache', where='time < %d' % expire_seconds)
total_after = sql_count_id(conn_iredapd, 'log_smtp_auth')

logger.info("* Remove expired smtp authentication log: "
            "%d removed, %d left." % (total_before - total_after, total_after))
