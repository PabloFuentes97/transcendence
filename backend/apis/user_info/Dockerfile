FROM python:3.8-bullseye

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Install necessary packages and dependencies
RUN pip install --no-build-isolation setuptools wheel

# Copy requirements file
COPY requirements.txt /usr/bin/requirements.txt

# Install dependencies from requirements file, excluding autobahn
RUN pip install --no-build-isolation --use-pep517 --no-cache-dir -r /usr/bin/requirements.txt 
#&& \ pip install autobahn

COPY . .

COPY ./entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

COPY ./wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

CMD ["/bin/bash", "/usr/bin/entrypoint.sh"]

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]