# Copyright 2019 The Kubernetes Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from kubernetes import client, config


def create_deployment(apps_v1_api):
    container = client.V1Container(
        name="deployment",
        image="gcr.io/google-appengine/fluentd-logger",
        image_pull_policy="Never",
        ports=[client.V1ContainerPort(container_port=5678)],
    )
    # Template
    template = client.V1PodTemplateSpec(
        metadata=client.V1ObjectMeta(labels={"app": "deployment"}),
        spec=client.V1PodSpec(containers=[container]))
    # Spec
    spec = client.V1DeploymentSpec(
        replicas=1,
        template=template)
    # Deployment
    deployment = client.V1Deployment(
        api_version="apps/v1",
        kind="Deployment",
        metadata=client.V1ObjectMeta(name="deployment"),
        spec=spec)
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    apps_v1_api.create_namespaced_deployment(
        namespace="default", body=deployment
    )


def create_service():
    core_v1_api = client.CoreV1Api()
    body = client.V1Service(
        api_version="v1",
        kind="Service",
        metadata=client.V1ObjectMeta(
            name="service-example"
        ),
        spec=client.V1ServiceSpec(
            selector={"app": "deployment"},
            ports=[client.V1ServicePort(
                port=5678,
                target_port=5678
            )]
        )
    )
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    core_v1_api.create_namespaced_service(namespace="default", body=body)


def create_ingress(networking_v1_beta1_api):
    body = client.NetworkingV1beta1Ingress(
        api_version="networking.k8s.io/v1beta1",
        kind="Ingress",
        metadata=client.V1ObjectMeta(name="ingress-example", annotations={
            "nginx.ingress.kubernetes.io/rewrite-target": "/"
        }),
        spec=client.NetworkingV1beta1IngressSpec(
            rules=[client.NetworkingV1beta1IngressRule(
                host="boddulabs.com",
                http=client.NetworkingV1beta1HTTPIngressRuleValue(
                    paths=[client.NetworkingV1beta1HTTPIngressPath(
                        path="/",
                        backend=client.NetworkingV1beta1IngressBackend(
                            service_port=5678,
                            service_name="service-example")

                    )]
                )
            )
            ]
        )
    )
    # Creation of the Deployment in specified namespace
    # (Can replace "default" with a namespace you may have created)
    networking_v1_beta1_api.create_namespaced_ingress(
        namespace="default",
        body=body
    )


def main():
    # Fetching and loading local Kubernetes Information
    config.load_kube_config()
    apps_v1_api = client.AppsV1Api()
    networking_v1_beta1_api = client.NetworkingV1beta1Api()

    create_deployment(apps_v1_api)
    create_service()
    create_ingress(networking_v1_beta1_api)


if __name__ == "__main__":
    main()
