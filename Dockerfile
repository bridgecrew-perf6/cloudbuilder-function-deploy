FROM gcr.io/google.com/cloudsdktool/cloud-sdk:latest

COPY function_deploy.py /usr/bin
ENTRYPOINT ["/usr/bin/function_deploy.py"]
