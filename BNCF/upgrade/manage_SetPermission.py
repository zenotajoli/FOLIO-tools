import pathlib
import requests
import json
import argparse
from folioclient.FolioClient import FolioClient

parser = argparse.ArgumentParser()
parser.add_argument("operation", help="backup or restore")
parser.add_argument("path", help="result file path (backup); take data from this file (restore)")
parser.add_argument("okapi_url", help="url of your FOLIO OKAPI endpoint.")
parser.add_argument("tenant_id", help="id of the FOLIO tenant")
parser.add_argument("username", help=("the api user"))
parser.add_argument("password", help=("the api users password"))
parser.add_argument("set_name", help="Name of set of permissions")

args = parser.parse_args()
folio_client = FolioClient(args.okapi_url, args.tenant_id, args.username, args.password)
okapiHeaders = folio_client.okapi_headers

if str(args.operation) == 'backup':
      path = "/perms/permissions?length=2000"
      req = requests.get(args.okapi_url+path,
                        headers=okapiHeaders)
      permission_resp = json.loads(req.text)
      perms= []
      for p in permission_resp["permissions"]:
            try:
                  if p['displayName'] == args.set_name:
                        perms.append(p['id'])
            except:
                  continue

      print("Total permissions: {}, Permissions fetched:{}"
            .format(permission_resp["totalRecords"], len(perms)))
      print(perms)
      path = "/perms/permissions/{}".format(perms[0])
      req = requests.get(args.okapi_url + path,
                        headers=okapiHeaders)
      perm_set = json.loads(req.text)
      del perm_set["childOf"]
      del perm_set["grantedTo"]
      del perm_set["dummy"]
      with open(args.path, 'w+') as settings_file:
            settings_file.write(json.dumps(perm_set))

if str(args.operation) == 'restore':
      with open(args.path) as settings_file:
            perm_set = json.load(settings_file)
            req = requests.put(args.okapi_url + path,
                              data=json.dumps(perm_set),
                              headers=okapiHeaders)
            print(req.status_code)
            if(req.status_code == 422):
                  print(req.text)
