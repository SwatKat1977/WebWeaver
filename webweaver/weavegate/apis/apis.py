'''
1) Token (optional to even automate)
POST /tokens/register

Honestly? You can even:
 hardcode tokens in DB for now

No need to overbuild this yet.

 2) Session lifecycle
POST /sessions/start
POST /sessions/heartbeat   (optional but highly recommended)

 You can actually skip end for MVP
(because expiry handles crashes and normal exits)

 3) Open project (this is the core endpoint)
POST /projects/{id}/open

This does:

checks lock
creates lock if available
returns:
editable OR read-only
lock owner info
maybe version

 This is your most important endpoint

 4) Download project
GET /projects/{id}/content

Returns:

zip / json / whatever your solution format is
 5) Upload project
POST /projects/{id}/content

Only allowed if:

caller owns lock
 6) Close project (release lock)
POST /projects/{id}/close
'''
