FROM python:3.8-bullseye

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

COPY requirements.txt .


RUN pip install --no-cache-dir -r requirements.txt

COPY . .

COPY ./entrypoint.sh /usr/bin/entrypoint.sh
RUN chmod +x /usr/bin/entrypoint.sh

COPY ./wait-for-it.sh wait-for-it.sh
RUN chmod +x wait-for-it.sh

CMD ["/bin/bash", "/usr/bin/entrypoint.sh"]

#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]