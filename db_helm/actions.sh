# https://phoenixnap.com/kb/postgresql-kubernetes

kubectl apply -f ./postgres-pv.yaml
kubectl apply -f ./postgres-pvc.yaml

helm install psql-smth bitnami/postgresql --set persistence.existingClaim=postgresql-pv-claim --set volumePermissions.enabled=true

# psql-smth-postgresql.default.svc.cluster.local
# psql-smth-postgresql

export POSTGRES_PASSWORD=$(kubectl get secret --namespace default psql-smth-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)

kubectl run psql-smth-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:15.1.0-debian-11-r12 --env="PGPASSWORD=$POSTGRES_PASSWORD" --command -- psql --host psql-smth-postgresql -U postgres -d postgres -p 5432

kubectl run psql-smth-postgresql-client --rm --tty -i --restart='Never' --namespace default --image docker.io/bitnami/postgresql:15.1.0-debian-11-r12 --env="PGPASSWORD=test" --command -- psql --host psql-smth-postgresql -U program -d postgres -p 5432
