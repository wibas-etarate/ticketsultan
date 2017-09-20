# ticketsultan

ticketsultan is a testproject for playing with google cloud services

#### You will find..
- many bugs
- a lot of useless stuff
- undocumented parts
- and furthermore a mountain of refactoring ahead



## How to run all that stuff localy?
###Run it from Google Cloud Console

	dev_appserver.py app.yaml

## Importand Endpoints
 ### Backend
    /admin/					#Admin UI
    /admin/sources/				#View and edit sources
    /admin/init				#Preinitialization
    /admin/parser/				#Parse sources
    /admin/parser/cron			#CRON Jobs
  ### Frontend
    /					#Frontend
    /search/				#Search Details


## Deployment to google cloud
    gcloud app deploy app.yaml queue.yaml cron.yaml

## Run it local
    dev_appserver.py app.yaml
    
## Run it with Visual Studio Code
- install Visual Studio Code
- take the configuration files from .vscode
- change the configuration to your needs

### tasks.json
   
   ```{
    "version": "0.1.0",
    "command": "python",
    "isShellCommand": true,
    "showOutput": "always",
    "args": [
        "/[PATH TO GOOGLE CLOUD SDK]/google-cloud-sdk/bin/dev_appserver.py",
        "--log_level=info",
        "--python_startup_script=${workspaceRoot}/pydev_startup.py",
        "--automatic_restart=no",
        "--search_indexes_path=${workspaceRoot}/datastore/",
        "--max_module_instances=default:1",
        "${workspaceRoot}/app.yaml"
    ]
    }```


