# Asynchttp Server

1. Ansynchronous Server running on top of gevent, and Flask
2. Requires Docker 1.12+
3. To run this project, all you need to do is docker-compose up
4. Url will be reacheable via `http://<docker‐host>:8080`
5. There is also a stats page reachable at `http://<docker‐host>:8080/stats/`
6. Downloadable files need to reside in the assets folder
7. To download the file, all you need to is `http://<docker‐host>:8080/download/filename_in_assets_directory.mov
8. Range requests are supported in both url and Range headers
9. Please see RFC2616 https://www.ietf.org/rfc/rfc2616.txt for more details on Range Requests
