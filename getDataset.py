import json
def get_dataset(project_id, location, dataset_id):
    """Gets any metadata associated with a dataset.

    See https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/healthcare/api-client/v1/datasets
    before running the sample."""
    # Imports the Google API Discovery Service.
    from googleapiclient import discovery

    api_version = "v1"
    service_name = "healthcare"
    # Returns an authorized API client by discovering the Healthcare API
    # and using GOOGLE_APPLICATION_CREDENTIALS environment variable.
    client = discovery.build(service_name, api_version)

    # TODO(developer): Uncomment these lines and replace with your values.
    # project_id = 'my-project'  # replace with your GCP project ID
    # location = 'us-central1'  # replace with the dataset's location
    # dataset_id = 'my-dataset'  # replace with your dataset ID
    dataset_name = "projects/{}/locations/{}/datasets/{}".format(
        project_id, location, dataset_id
    )

    datasets = client.projects().locations().datasets()
    dataset = datasets.get(name=dataset_name).execute()

    print("Name: {}".format(dataset.get("name")))
    print("Time zone: {}".format(dataset.get("timeZone")))

    return dataset

def search_resources_post(project_id, location, dataset_id, fhir_store_id, query_key,query_value):
    """
    Searches for resources in the given FHIR store. Uses the
    _search POST method and a query string containing the
    information to search for. In this sample, the search criteria is
    'family:exact=Smith' on a Patient resource.

    See https://github.com/GoogleCloudPlatform/python-docs-samples/tree/main/healthcare/api-client/v1/fhir
    before running the sample."""
    # Imports Python's built-in "os" module
    import os

    # Imports the google.auth.transport.requests transport
    from google.auth.transport import requests

    # Imports a module to allow authentication using a service account
    from google.oauth2 import service_account

    # Gets credentials from the environment.
    credentials = service_account.Credentials.from_service_account_file(
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"]
    )
    scoped_credentials = credentials.with_scopes(
        ["https://www.googleapis.com/auth/cloud-platform"]
    )
    # Creates a requests Session object with the credentials.
    session = requests.AuthorizedSession(scoped_credentials)

    # URL to the Cloud Healthcare API endpoint and version
    base_url = "https://healthcare.googleapis.com/v1"

    # TODO(developer): Uncomment these lines and replace with your values.
    # project_id = 'my-project'  # replace with your GCP project ID
    # location = 'us-central1'  # replace with the parent dataset's location
    # dataset_id = 'my-dataset'  # replace with the parent dataset's ID
    # fhir_store_id = 'my-fhir-store' # replace with the FHIR store ID
    url = "{}/projects/{}/locations/{}".format(base_url, project_id, location)

    fhir_store_path = "{}/datasets/{}/fhirStores/{}/fhir".format(
        url, dataset_id, fhir_store_id
    )

    resource_path = "{}/Patient/_search?{}:exact={}".format(fhir_store_path,query_key,query_value)

    # Sets required application/fhir+json header on the request
    headers = {"Content-Type": "application/fhir+json;charset=utf-8"}

    response = session.post(resource_path, headers=headers)
    response.raise_for_status()

    resources = response.json()
    print(
        "Using POST request, found a total of {} Patient resources:".format(
            resources["total"]
        )
    )

    # print(json.dumps(resources, indent=2))

    return resources



# get_dataset("intricate-will-343721","us-central1","Test_1")

h = search_resources_post("intricate-will-343721", "us-central1","Test_1", "5810test","resourceType","Bundle")
# from json2txttree import json2txttree
# print(json2txttree(h))
# print(h['entry'][0]["resource"]['name'][0]['family'])
def pasrseResult(result,key):
    res = []
    total = result['total']
    if len(key) == 1:
        for i in range(total):
            print(result['entry'][i]["resource"][key[0]])
            res.append(result['entry'][i]["resource"][key[0]])
    elif len(key) == 2:
        for i in range(total):
            print(result['entry'][i]["resource"][key[0]][0][key[1]])
            res.append(result['entry'][i]["resource"][key[0]][0][key[1]])
    return res

import pandas as pd
bD = pasrseResult(h,['birthDate'])
nm = pasrseResult(h,['name','family'])
gd = pasrseResult(h,['gender'])


df = pd.DataFrame([nm,bD,gd])
df = df.transpose()
print(df)