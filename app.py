import os
import datetime
import platform
from src.Pubsub import Pubsub
from src.Worker import Worker
from src.Mailer import Mailer
from src.ApiClient import ApiClient
from src.ProcessorServer import ProcessorServer
from sanic import Sanic, response

VERSION = 'v0.2'

app = Sanic(__name__)

w = Worker()
date, nodename = str(datetime.datetime.now()), str(platform.node())
endpoint, user, pasw = os.getenv("ENDPOINT"), os.getenv("API_USER"), os.getenv("API_PASS")

@app.after_server_start
async def after_server_start(app, loop):
    w.logger.info(f"\nApp listening at port {os.environ['PORT']}")
    Pubsub.run_pubsub_watch(w.logger)


@app.route('/request', methods=['POST'])
async def request(req):
    mailer = Mailer(w.logger, w.logs_file, os.getenv("MAILER_FROM"), os.getenv("MAILER_TO"), os.getenv("MAILER_PASS"))
    processor_server = ProcessorServer(w)
    result = w.run(processor_server, mailer)
    print(result)

    bodytext = f'{w.msg_from_req(req)} \nFinished ok: {VERSION} {date} {nodename} \n {result} \n'
    for contactors in result:
        for contractor in contactors.values():
            resp = ApiClient.send_payload(contractor, endpoint, user, pasw)
            w.logger.info(f'{resp.text} \n {resp}')
            bodytext += resp.text + '\n'

    mailer.send_email(bodytext)

    return response.text(body='', status=200)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ['PORT']), motd=False, access_log=False)
