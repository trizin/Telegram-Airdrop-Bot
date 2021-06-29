FROM python:3.7-alpine

WORKDIR /app
COPY requirements.txt requirements.txt
RUN apk add --no-cache gcc musl-dev jpeg-dev zlib-dev libffi-dev cairo-dev pango-dev gdk-pixbuf-dev openssl-dev
ENV CRYPTOGRAPHY_DONT_BUILD_RUST=1
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
COPY . .
CMD ["python3","bot.py"]