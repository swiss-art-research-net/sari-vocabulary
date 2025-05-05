FROM python:3.8

# Install system dependencies
RUN apt-get -qq update && \
    apt-get -q -y upgrade && \
    apt-get install -y \
        sudo \
        curl \
        wget \
        locales && \
    locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

ENV LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Set the timezone
RUN ln -sf /usr/share/zoneinfo/Europe/Zurich /etc/localtime
ENV TZ=Europe/Zurich

# Install task runner (http://taskfile.dev)
RUN sh -c "$(curl -sSL https://taskfile.dev/install.sh)" -- -d

VOLUME /data
WORKDIR /scripts

CMD ["tail", "-f", "/dev/null"]