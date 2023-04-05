From project root directory:

* sudo docker build --force-rm -t ya-serv-container -f ./serverless-container/build/Dockerfile .

* sudo docker run -p 8080:8080 -e PORT=8080 -e EMAIL=XXX -e PASS=XXX -e SERVER=imap.XXX.com \
      MAILER_FROM=XXX -e MAILER_PASS=XXX -e MAILER_TO=XXX  -e PUBSUB_TOPIC=projects/project-name/topics/XXX API_PASS=XXX \
      -e ENDPOINT="http://XXX" ya-serv-container

* curl -X POST -d '{"message":"my message text here"}' http://localhost:8080/request

* sudo docker tag ya-serv-container cr.yandex/REGISTRY_ID/mail-processor:v1.XXX

* docker image push cr.yandex/REGISTRY_ID/mail-processor:v1.XXX
