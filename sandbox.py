import os
from pathlib import Path

from src.Worker import Worker
from src.ProcessorLocal import ProcessorLocal
from src.ApiClient import ApiClient

worker = Worker()
processor_local = ProcessorLocal(worker)

## SINGLE FILE PROCESSING ##
# path = '/home/Downloads/'
# file = 'letter.eml'
# result = ProcessorLocal.process_eml(path + file)
# print(result)

## BATCH FILE PROCESSING ##
file_list = []
# for n, path in enumerate(list(Path('/home/Documents/data/data/parsing').rglob('*.eml'))[:]):
for n, path in enumerate(['/home/username/Downloads/email.eml']):
    print(f"\n\n***{n} {str(path).split('/')[-1]}****\n\n")
    result = processor_local.process_eml(path)
    print(result)

    # SENDING RESULTS VIA API
    r = ''
    for contactors in result:
        for contractor in contactors.values():
            resp = ApiClient.send_payload(contractor, os.getenv("ENDPOINT"), os.getenv("API_USER"), os.getenv("API_PASS"))
            r = resp.text
            worker.logger.info(f'{r} \n {resp}')
