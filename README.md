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
    /admin/init					#Preinitialization
    /admin/parser/				#Parse sources
    /admin/parser/cron				#CRON Jobs
  ### Frontend
    /						#Frontend
    /search/					#Search Details


## Deployment to google cloud
    gcloud app deploy app.yaml queue.yaml cron.yaml

## Run it local
    dev_appserver.py app.yaml
    
## Run it with Visual Studio Code
- install Visual Studio Code

