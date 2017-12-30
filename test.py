import requests
import time
import json

status_url = {}
for i in range(25):
    data = {'file': open('./tests/test_recipe.json', 'rb')}
    response = requests.post(url='http://127.0.0.1:5000/', files=data)
    print(response.content)
    status_url[response.headers['status']] = False  # is done is false

# check the status
finished = []
total = len(status_url)
while total > len(finished):
    for status, is_done in status_url.iteritems():
        if is_done:
            continue
        progress = requests.get('http://127.0.0.1:5000' + status)
        content = json.loads(progress.content)
        if content['state'] == 'PENDING':
            print('task is pending at {}'.format(status))
        elif content['state'] == 'STARTED':
            print('task is still running at {}'.format(status))
        else:
            finished.append(status)
            status_url[status] = True
            print('task is finished at {} ({} of {}).'.format(status,
                                                              len(finished),
                                                              total))
        time.sleep(1)
        # Here is how you can get the results from the response
        # print('results:')
        # for grid in content['result']:
        #     for count, pt in enumerate(grid['analysis_points']):
        #         print('sensor #{}; location: {}'.format(count, pt['location']))
        #         for values in pt['values'][0]:
        #             for hour, value in values.iteritems():
        #                 print('\thour: {} >> result: {}'.format(hour, value[0]))
