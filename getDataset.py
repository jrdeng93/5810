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

def search_resources_post(project_id, location, dataset_id, fhir_store_id, query_key,query_value,dataType):
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
        "./intricate-will-343721-0ef3bfb5b7e4.json"
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

    resource_path = "{}/{}/_search?{}:contains={}".format(fhir_store_path,dataType,query_key,query_value)

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


patient = search_resources_post("intricate-will-343721", "us-central1","Test_1", "5810test","resourceType","Patient","Patient")
# for k in patient['resource'].keys():
#     print(k)
#print(patient['entry'][0]["resource"]["address"][0]['country'])
# exit()
# print(len(patient['entry']))
# exit()
def pasrsePatient(result,key):
    res = []
    total = result['total']
    if len(key) == 1:
        for i in range(total):
            try:
                res.append(result['entry'][i]["resource"][key[0]])
            except:
                res.append("none")

    elif len(key) == 2:
        for i in range(total):
            try:
            # print(result['entry'][i]["resource"][key[0]][0][key[1]])
                res.append(result['entry'][i]["resource"][key[0]][0][key[1]])
            except:
                res.append("none")
    return res

obs = search_resources_post("intricate-will-343721", "us-central1","Test_1", "5810test","Observation","20f8110a-d99c-4d2d-a177-20a70870a383","Observation")
# for k in obs.keys():
#     print(k)
# print(obs['entry'])
# print(len(obs['entry']))
# exit()

def parseObservation(result,key):
    res = []
    total =100#len(result['entry'])
    if len(key) == 1:
        for i in range(total):
            try:
                res.append(result['entry'][i]["resource"][key[0]])
            except:
                res.append("none")

    elif len(key) == 2:
        for i in range(total):
            try:
                # print(result['entry'][i]["resource"][key[0]][key[1]])
                res.append(result['entry'][i]["resource"][key[0]][key[1]])
            except:
                res.append("none")

    return res


import pandas as pd
#####Generate Patient Dataframe
bD = pasrsePatient(patient,['birthDate'])
nm = pasrsePatient(patient,['name','family'])
gd = pasrsePatient(patient,['gender'])
id = pasrsePatient(patient,['id'])
adds_city = pasrsePatient(patient,['address','city'])
adds_state = pasrsePatient(patient,['address','state'])
adds_country = pasrsePatient(patient,['address','country'])
df = pd.DataFrame([id,nm,bD,gd,adds_city,adds_state,adds_country])
df = df.transpose()
print(df)

#####Generate Observation Dataframe
obsMap = {"id":['subject','reference'],"code":['code','text'],"value":["valueQuantity","value"],"unit":["valueQuantity","unit"]}
id = parseObservation(obs,obsMap["id"])
newId = []
for i in id:
    newId.append(i[8:])
id = newId
code = parseObservation(obs,obsMap["code"])
value = parseObservation(obs,obsMap["value"])
unit = parseObservation(obs,obsMap["unit"])
df = pd.DataFrame([id,code,value,unit])
df = df.transpose()
print(df)
#### query gender = male
#male_Data = search_resources_post("intricate-will-343721", "us-central1","Test_1", "5810test","gender","male")