# Seldon Core

Seldon Core, an open source framework agnostic serving platform built for speed and scale, capable of running models on Kubernetes at massive scale. Seldon handles scaling to thousands of production machine learning models and provides advanced machine learning capabilities out of the box including Advanced Metrics, Request Logging, Explainers, Outlier Detectors, A/B Tests, Canaries and more. Seldon Core serves models built in any open-source or commercial model building framework. Seldon core converts your ML models (Tensorflow, Pytorch, H2o, etc.) or language wrappers (Python, Java, etc.) into production REST/GRPC microservices.

In this example we will deploy sklearn iris classification model using two approaches.

1. Seldon default protocol
2. V2 protocol

## Installation

Pre-requsities

* Install [Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
* Install [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installing-from-release-binaries)
* Install [Kubectl](https://kubernetes.io/docs/tasks/tools/#kubectl)
* Install [Helm](https://helm.sh/docs/intro/install/)

After installing above follow this guide to deploy seldon using kind : [Install Locally](https://docs.seldon.io/projects/seldon-core/en/latest/install/kind.html#set-up-kind)

## Run

### Simple Example

```yaml
apiVersion: machinelearning.seldon.io/v1alpha2
kind: SeldonDeployment
metadata:
  name: sklearn
spec:
  predictors:
    - graph:
        name: classifier
        implementation: SKLEARN_SERVER
        modelUri: gs://seldon-models/v1.14.0-dev/sklearn/iris
      name: default
      replicas: 1
      svcOrchSpec:
        env:
          - name: SELDON_LOG_LEVEL
            value: DEBUG

```

```bash
# setup cluster using kind
kind create cluster --name seldon
# make seldon as default namespace
kind cluster-info --context kind-seldon
# install istiol
istioctl install --set profile=demo -y 
# namespace label istio-injection=enabled instructs Istio to automatically inject proxies alongside anything we deploy in that namespace.
kubectl label namespace default istio-injection=enabled
# create Istio Gateway
kubectl apply -f - << END
apiVersion: networking.istio.io/v1alpha3
kind: Gateway
metadata:
  name: seldon-gateway
  namespace: istio-system
spec:
  selector:
    istio: ingressgateway # use istio default controller
  servers:
  - port:
      number: 80
      name: http
      protocol: HTTP
    hosts:
    - "*"
END
# create namepsace for seldon core
kubectl create namespace seldon-system
# using istio as ingress install seldon core in our cluster
helm install seldon-core seldon-core-operator --repo https://storage.googleapis.com/seldon-charts --set istio.enabled=true --set usageMetrics.enabled=true --namespace seldon-system
# monitor till seldon controller is running
kubectl rollout status deploy/seldon-controller-manager -n seldon-system
# forward any traffic from port 8003 on your local machine to port 80 inside your cluster
kubectl port-forward -n istio-system svc/istio-ingressgateway 8003:80
# deploy our ML application to Kubernetes cluster
kubectl apply -f iris.yaml
# monitor until successful rollout
kubectl rollout status deploy/$(kubectl get deploy -l seldon-deployment-id=sklearn -o jsonpath='{.items[0].metadata.name}')
```

Swagger Docs: [http://localhost:8003/seldon/default/sklearn/api/v1.0/doc/](http://localhost:8003/seldon/default/sklearn/api/v1.0/doc/)

Test Endpoint

```bash
curl -s -X POST -H 'Content-Type: application/json' -d '{"data":{"ndarray":[[5.964, 4.006, 2.081, 1.031]]}}' http://localhost:8003/seldon/default/sklearn/api/v1.0/predictions  | jq .
python3 test_endpoint.py
# using httpie library
echo '{"data":{"ndarray":[[5.964, 4.006, 2.081, 1.031]]}}' | http :8003/seldon/default/sklearn/api/v1.0/predictions
```

Delete the ML application

```bash
# delete our deployment
kubectl delete -f iris.yaml
```

### Simple Example using V2 protocol

```yaml
apiVersion: machinelearning.seldon.io/v1
kind: SeldonDeployment
metadata:
  name: sklearn
spec:
  name: iris
  protocol: v2
  predictors:
    - graph:
        children: []
        implementation: SKLEARN_SERVER
        modelUri: gs://seldon-models/sklearn/iris-0.23.2/lr_model
        name: classifier
      name: default
      replicas: 1
```

Follow the same commands above replacing `iris.yaml` with `iris_v2.yaml`.

Test Endpoint

```bash
python3 test_endpoint_v2.py
```

Delete the ML application

```bash
# delete our deployment
kubectl delete -f iris_v2.yaml
```

Seldon Core provides lot many benefits, some of them include

* [MLOps: Scaling and Monitoring and Observability](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#mlops-scaling-and-monitoring-and-observability)
* [A/B Testing and Progressive Rollouts](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#ab-tests-and-progressive-rollouts)
* Easy way to containerise ML models using [language wrappers](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#python-language-wrapper-examples) or [pre-packaged inference servers](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#prepackaged-inference-server-examples).
* Out of the box endpoints which can be tested through Swagger UI, Seldon Python Client or Curl / GRPCurl
* [Batch Processing](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#batch-processing-with-seldon-core)
* [Drift detection, Prediction explainers, Outlier detection](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#advanced-machine-learning-monitoring)
* Cloud agnostic and [tested](https://docs.seldon.io/projects/seldon-core/en/latest/examples/notebooks.html#cloud-specific-examples) on AWS EKS, Azure AKS, Google GKE, Alicloud, Digital Ocean and Openshift.
and many more....
