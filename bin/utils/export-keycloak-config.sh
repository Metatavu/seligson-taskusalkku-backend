#/bin/sh

REALM=seligson
CONTAINER_ID=$(docker ps -q --filter ancestor=quay.io/keycloak/keycloak:latest)

docker exec -e JDBC_PARAMS='?useSSL=false'  -ti $CONTAINER_ID  /opt/jboss/keycloak/bin/standalone.sh -Djboss.socket.binding.port-offset=102 -Dkeycloak.migration.action=export -Dkeycloak.migration.provider=singleFile -Dkeycloak.migration.realmName=$REALM -Dkeycloak.migration.usersExportStrategy=REALM_FILE -Dkeycloak.migration.file=/tmp/my_realm.json
docker cp $CONTAINER_ID:/tmp/my_realm.json /tmp/my_realm.json
cp /tmp/my_realm.json src/tests/data/kc.json
