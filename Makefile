# ---------------------------------------------------------
# [  INCLUDES  ]
# override to whatever works on your system

include ./Makefile.in.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# override to whatever works on your system

APPLICATION := main.service:app
ENTRYPOINT := $(PYTHON) $(DIR_SRC)/main/app.py

include ./Makefile.targets.mk


# ---------------------------------------------------------
# [  TARGETS  ]
# keep your targets here


.PHONY: setup
setup:
	$(call log, setting up the project)
	@echo "first, set up all secrets"
	@echo "check the secrets dir and edit them"
	@python ${DIR_CONFIG}/make_secrets.py
	@echo ""
	@echo "now, you have to do the following:"
	@echo ""
	@echo "1. set up the database"
	@echo "\tyou MUST set the DATABASE_URL"
	@echo "\tthen, run 'make initdb' - it will populate the schema"
	@echo ""
	@echo "2. set up the Telegram"
	@echo "\tobtain the HTTPS host (i.e. using ngrok)"
	@echo "\tset the HOST to the HTTPS URL"
	@echo "\tset the PORT to 443"
	@echo "\tobtain the token from @BotFather"
	@echo "\tset the TELEGRAM_BOT_TOKEN to that token"
	@echo ""
	@echo "3. 'make run' will run the web server"
	@echo "\tgo to localhost:8000 and set the webhook to the new ngrok url"
	@echo ""
	@echo "-*- the end -*-"


.PHONY: migrations
migrations::
	alembic revision --autogenerate


.PHONY: migrate
migrate::
	alembic upgrade head
