FROM python:3.8-bullseye

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

#Copy Django game app
COPY . .

# Copy database init dependencies
COPY ./database.ini /usr/bin/database.ini
COPY ./connect_postgres.py /usr/bin/connect_postgres.py
RUN chmod +x /usr/bin/connect_postgres.py

# Install necessary packages and dependencies
COPY ./requirements.txt /usr/bin/requirements.txt
RUN pip install --no-build-isolation setuptools wheel
RUN pip install --no-build-isolation --use-pep517 --no-cache-dir -r /usr/bin/requirements.txt 

COPY ./entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

CMD ["/bin/bash", "/usr/bin/entrypoint.sh"]