FROM ubuntu:20.04

# Install dependent commands
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y curl git python3 zlib1g-dev libglfw3-dev libsdl2-dev cmake qtbase5-dev build-essential rsync && rm -rf /var/lib/apt/lists/*

# Create pdraw user
RUN useradd -ms /bin/bash pdraw
USER pdraw
WORKDIR /home/pdraw

# Install repo command
RUN mkdir -p bin
RUN curl https://storage.googleapis.com/git-repo-downloads/repo > bin/repo

RUN chmod a+x bin/repo && sed -i.bak -e 's;#!/usr/bin/env python$;#!/usr/bin/env python3;' bin/repo

# Install groundsdk-tools
RUN mkdir -p /home/pdraw/code/groundsdk-tools
WORKDIR /home/pdraw/code/groundsdk-tools

RUN /home/pdraw/bin/repo init -u https://github.com/Parrot-Developers/groundsdk-tools-manifest && /home/pdraw/bin/repo sync
#RUN chmod u+x -R /home/pdraw/code/groundsdk-tools


RUN yes "y" | ./build.sh -p groundsdk-linux -t build -j/1

ENTRYPOINT [ "./out/groundsdk-linux/staging/native-wrapper.sh" ]
# CMD ["vmeta-extract", "--help"]