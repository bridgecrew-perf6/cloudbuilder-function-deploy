[![CodeFactor](https://www.codefactor.io/repository/github/vwt-digital/cloudbuilder-function-deploy/badge)](https://www.codefactor.io/repository/github/vwt-digital/cloudbuilder-function-deploy)

# Function Deploy

This cloudbuilder simplifies the deployment of a cloud function together with applying an invoker role for the function.

The cloudbuilder image can be used in the cloudbuild.yaml

`- name: 'eu.gcr.io/{cloudbuilders}/cloudbuilder-function-deploy'`

The syntax for the function deploy script is identical to the syntax of the standard `gcloud function deploy` command except for the `--invoker` parameter. 

The `--invoker` params specifies which account should be given the `roles/cloudfunctions.invoker` role. The `--invoker` parameter may be specified multiple times.

When the `--invoker` tag is omitted appying of the invoker role is skipped.



## Deployment variables

Deployment variables for the `gcloud function deploy` can be specified in 3 ways (in sequence of priority)
1.  Command line parameters. Parameters specified on the `function-deploy.py` have the highest priority. These values override the values from option 2) and 3)
2.  Additional values van be specified in a  `deploy.json` file in the same directory where the cloud function resides. These values override values specified at 3)
3.  By default, the following options are added to the command line:
    - `--max-instances=1`
    - `--memory=128MB`
    - `--region=europe-west1`
    - `--security-level=secure-always` (if `--trigger-http` is defined)

## Example
The example below shows a `cloudbuild.yaml` fragment
```yaml
  - name: 'eu.gcr.io/{cloudbuilders}/cloudbuilder-function-deploy'
    id: 'Deploy my important function'
    entrypoint: 'bash'
    args:
      - '-c'
      - |
        echo "PYTHON_VAR = 'some_value'" > config.py
        
        function_deploy.py ${PROJECT_ID}-my-important-func \
        --project="${PROJECT_ID}" \
        --set-env-vars=VARIABLE="value" \
        --invoker="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
        --trigger-http \
```
and `deploy.json` file
 ```json
{
   "entry-point": "handler",
   "memory": "256MB",
   "runtime": "python38"
}
```

### The example above will result in:
```shell
gcloud function deploy ${PROJECT_ID}-my-important-func \
        --project="${PROJECT_ID}" \
        --set-env-vars=VARIABLE="value" \
        --invoker="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
        --trigger-http \
        --entry-point=handler \
        --memory=256MB \
        --runtime=python38 \
        --region=europe-west1
```
and the 
```shell
gcloud functions set-iam-policy ${PROJECT_ID}-my-important-func \
	--project="${PROJECT_ID}" \
	--region=europe-west1
```
will be used with the IAM bindings as shown below
```json
{ "bindings":[
    { "role":"roles/cloudfunctions.invoker", 
      "members": ["serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com"]
} ] } 
```

# How To: Reuse Common Functionality
In programming, it often happens that we want to reuse code. But how will we go about doing this in cloud functions?

## Local Common Functions
In our cloud function repositories we structure code in the follow way:
```
my_repository
└───functions
    ├───common
    │   └───common_objects.py
    ├───some_cloud_function
    │   ├───main.py
    │   ├───deploy.json
    │   └───requirements.txt
    └───another_cloud_function
        ├───main.py
        ├───deploy.json
        └───requirements.txt
```

In this example you can see we have 2 functions: 'some_cloud_function', and 'another_cloud_function'.
If these functions share functionality, it can be a good idea to abstract that functionality 
away into a common folder. Here we put some object(s) (`common_objects.py`) that both functions 
use in the common folder, which when deployed correctly can be used by both functions.

In order to import this common folder onto the cloud correctly we will use `import_common.py` in our `cloudbuild.yaml`.

An example of such a deployment step could be:
```yaml
# Deploys some_cloud_function
- name: 'eu.gcr.io/{cloudbuilders}/cloudbuilder-function-deploy'
  id: 'Deploy some_cloud_function'
  entrypoint: 'bash'
  args:
    - '-c'
    - |
      import_common.py
      function_deploy.py ${PROJECT_ID}-some-cloud-function
  dir: 'my_repository/functions/some_cloud_function'
```

Here you can see that we first import the common functionality before 
deploying the function to the cloud with `function_deploy.py`.  This will make sure that 
the cloud has access to our common code when deploying.

Behind the scenes we actually copy the contents of the common folder into the folder of the function 
with a simple "treecopy". After some much-needed [preprocessing](#python-imports).

### Arguments
Our `import_common.py` has a few **optional** arguments that we can use in case our file structure differs 
from the example.

| Field              | Description                                  | Default                                                                                                                                                                   | Required |
| :----------------- | :------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :------: |
| --function         | The path of the cloud function.              | `.`                                                                                                                                                                       | No       |
| --common           | The path of the common folder.               | `../common`                                                                                                                                                               | No       |
| --common-package   | The base package used in the common code.    | `functions.common`                                                                                                                                                        | No       |
| --function-package | The base package used by the cloud function. | --common-package (`functions.common`) where --common directory name (`common`) is replaced by --function directory name (`some_function`). E.g. `functions.some_function` | No       |

### Python Imports
Now you might think: won't my function's imports be all wrong after the common folder's contents
are copied into it? This is where the preprocessing comes in. The `import_common.py` will first scan all
the function's code and tries to correct the imports.

It does this by replacing all `--common-package` text to `--function-package` text (**only** in the import lines).

E.g.
`my_repository/functions/some_cloud_function/main.py`
```python
from functions.common.common_objects import CommonObject
import functions.common


def main():
    common = CommonObject()

```

Will become:
```python
from functions.some_cloud_function.common_objects import CommonObject
import functions.some_cloud_function


def main():
    common = CommonObject()

```