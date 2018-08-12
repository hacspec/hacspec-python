FROM ubuntu:18.04
MAINTAINER Franziskus Kiefer <franziskuskiefer@gmail.com>

# Pinned version of HACL* (F* and KreMLin are pinned as submodules)
ENV haclrepo https://github.com/mitls/hacl-star.git

# Define versions of dependencies
ENV opamv 4.05.0
ENV haclversion ff810f30ec62051f10ab242dab2bdb5f7c8678e6

# Create user.
RUN useradd -ms /bin/bash worker
WORKDIR /home/worker

# Install required packages and set versions
# Build F*, HACL*. Install a few more dependencies.
ENV OPAMYES true
ENV PATH "/home/worker/hacl-star/dependencies/z3/bin:/home/worker/hacl-star/dependencies/FStar/bin/:$PATH"
ENV FSTAR_HOME "/home/worker/hacl-star/dependencies/FStar"
ENV HACL_HOME "/home/worker/hacl-star/"
ADD setup.sh /tmp/setup.sh
ADD setup-root.sh /tmp/setup-root.sh
RUN bash /tmp/setup-root.sh

USER worker
RUN bash /tmp/setup.sh
