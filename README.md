<p align="center"><img src="assets/logo.jpeg" alt="Ocena" height="100px"></p>

<div align="center">
  <a href="https://travis-ci.com/Go-phie/ocena">
    <img src="https://travis-ci.com/Go-phie/ocena.svg?branch=master" alt="Build Status">
  </a>
</div>

# Ocena

Ocena basically means "Rating" in Polish. It is the service responsible for handling all ratings related issues for Gophie-web

```bash
# alembic autogenerate revision
alembic revision --autogenerate -m "Commit message"
```
## Development
- Manual
  ```bash
    pip install -r requirements.txt

    uvicorn main:app --debug
  ```
- Running using Docker
  - Create a .env file using env.example as sample

  - ```
    docker-compose up
    ```
  - Exec into the `ocena` container run alembic to create database tables
  `alembic upgrade head`

Visit http://localhost:8000/docs to interact with API
Visit http://localhost:4000 for Gophie Web
