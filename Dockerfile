FROM python:3.11-slim

#Create config and log folders
RUN mkdir /opt/autocracker
RUN mkdir /opt/autocracker/app
RUN mkdir /opt/autocracker/conf
RUN mkdir /opt/autocracker/log
RUN mkdir /opt/autocracker/schemas

WORKDIR /opt/autocracker

ADD ./app/* /opt/autocracker/app
ADD ./schemas/* /opt/autocracker/schemas
ADD ./conf/* /opt/autocracker/conf
COPY ./requirements.txt /opt/autocracker/requirements.txt
COPY ./run.py /opt/autocracker/run.py


# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "-u", "run.py"]