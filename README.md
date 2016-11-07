# Asynchttp Server


1. Ansynchronous Server running on top of gevent, and Flask
2. Requires Docker 1.12+
3. To run this project, all you need to do is docker-compose up
4. Url will be reacheable via http://<docker‐host>:8080
5. There is also a stats page reachable at http://<docker‐host>:8080/stats/
6. Supports Range Requests as specified in RFC2616 https://www.ietf.org/rfc/rfc2616.txt
