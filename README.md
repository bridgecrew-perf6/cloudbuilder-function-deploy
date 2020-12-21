[![CodeFactor](https://www.codefactor.io/repository/github/vwt-digital/cloudbuilder-function-deploy/badge)](https://www.codefactor.io/repository/github/vwt-digital/cloudbuilder-function-deploy)

# Combined deploy of function and invoker role

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
3.  By default the command line option `--region=europe-west1` is added to the command line

## Example
The example below shows a `cloudbuild.yaml` fragment
```
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
 ```
{
   "entry-point":"handler",
   "memory": "256MB",
   "runtime": "python38"
}
```

### The example above will result in:
``` 
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
```
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

