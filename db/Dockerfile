# pull official base image
FROM postgres:16-alpine

# Instala postgresql-client para poder usar pg_dump y pg_restore
RUN apk add --no-cache postgresql-client

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d
