# ticketsultan

ticketsultan is a testproject for playing with google cloud services

You will find..
- many bugs
- a lot of useless stuff
- undocumented parts
- and furthermore a mountain of refactoring ahead



## How to run all that stuff localy?
###Run it from Google Cloud Console

	dev_appserver.py app.yaml

## Importand Endpoints
    /admin/					#Admin UI
	/admin/init				#Preinitialization
	/admin/parse/			#Parse sources
	/						#Frontend


## Deployment to google cloud
    gcloud app deploy app.yaml queue.yaml cron.yaml
