# Subscription Tracker App

This app tracks my subscriptions to streaming services and shows stats such as
- cost of each subscription
- total cost per month
- total cost per year
- number of films/tv shows watched per month
- most frequently used service

REST API calls are used to
- insert, update, or delete services
- insert, update, or delete films/shows that have been watched

## Technologies
- Flask
- Python
- SQLite
- HTML

## Streaming Services
- Netflix
- Hulu
- Amazon Prime Video
- Peacock
- Disney+
- Crunchyroll
- Xfinity Stream
- Kanopy
- Tubi

## Enhancements
- SQLite doesn't enforce the length of a VARCHAR. If I used a database that does enforce the length, I could remove that extra validation check.
- Similar idea for float/decimal fields and the precision.

## Resources
- https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
