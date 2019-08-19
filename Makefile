
REPO_ROOT:=${CURDIR}

base: requirements.txt Dockerfile
	docker build -t olivaw/base -f Dockerfile .

run: base
	docker run \
		-v $(REPO_ROOT):/usr/src/app \
		-p 8080:8080 \
		olivaw/base \
		gunicorn -b :8080 olivaw.main:app
