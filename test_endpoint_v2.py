import json

import requests

inference_request = {
    "inputs": [
        {"name": "predict", "shape": [1, 4], "datatype": "FP32", "data": [[1, 2, 3, 4]]}
    ]
}

endpoint = "http://localhost:8003/seldon/default/sklearn/v2/models/infer"
response = requests.post(endpoint, json=inference_request)

print(json.dumps(response.json(), indent=2))
assert response.ok
