FROM haproxy:latest
USER root
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY monitor.sh /usr/local/bin/monitor.sh
RUN chmod +x /usr/local/bin/monitor.sh
CMD /usr/local/bin/monitor.sh & haproxy -f /usr/local/etc/haproxy/haproxy.cfg