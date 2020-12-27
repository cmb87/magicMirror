## Setup a Postgres (local test, only necessary when no other server available)
0.) Install mlfow and dependencies (assuming PostgreSQL + S3 storage):

        pip install mlflow boto3 psycopg2

1.) Install postgres docker: 

        docker run --name some-postgres -e POSTGRES_PASSWORD=123 -d -p 5432:5432 postgres

2.) Connect with shell:

        docker exec -it some-postgres sh

3.) Inside container create db: 

        createdb -U postgres mydb

