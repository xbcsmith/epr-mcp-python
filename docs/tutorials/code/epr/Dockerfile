# SPDX-FileCopyrightText: © 2025 Brett Smith <xbcsmith@gmail.com>
# SPDX-License-Identifier: Apache-2.0
#
# Builds the Event Provenance Registry server for the workshop.
#
# EPR does not publish an image, and its own Dockerfile produces a FROM scratch
# image with no time zone database, while the server always connects to Postgres
# with TimeZone=America/New_York. That server then exits at startup with
# "unknown time zone America/New_York". This file builds the same binary and
# adds the zoneinfo directory so it starts.
#
ARG EPR_REPO=https://github.com/xbcsmith/event-provenance-registry.git
ARG EPR_REF=f8f115b790c58b8fab3bfd47278e51e4f15e9f0e

FROM golang:1.25-trixie AS builder
ARG EPR_REPO
ARG EPR_REF
WORKDIR /build
ADD ${EPR_REPO}#${EPR_REF} .
RUN make clean && make linux

FROM scratch
COPY --from=builder /build/bin/epr-server /usr/local/bin/epr-server
COPY --from=builder /usr/share/zoneinfo /usr/share/zoneinfo
CMD ["/usr/local/bin/epr-server"]
