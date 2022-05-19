import requests
from pprint import pprint

print("Test using requests")

url = "http://localhost:8003/seldon/default/sklearn/api/v1.0/predictions"

data = '{"data": {"ndarray":[[1.0, 2.0, 5.0, 6.0]]}}'
headers = {
    "Content-type": "application/json",
}
r = requests.post(url, headers=headers, data=data)
pprint(r.content)

print("Test using Seldon Client (REST and GRPC)")

from seldon_core.seldon_client import SeldonClient
from seldon_core.utils import json_to_seldon_message

sc = SeldonClient(deployment_name="sklearn", namespace="default")

res = sc.predict(
    gateway="istio",
    gateway_endpoint="localhost:8003",
    transport="rest",
    raw_data={"data": {"ndarray": [[1.0, 2.0, 5.0, 6.0]]}},
)
print(res.response)
assert res.success == True


proto_raw_data = json_to_seldon_message(
    {"data": {"ndarray": [[5.964, 4.006, 2.081, 1.031]]}}
)
res = sc.predict(
    gateway="istio",
    gateway_endpoint="localhost:8003",
    transport="grpc",
    raw_data=proto_raw_data,
)
print(res)
assert res.success == True
