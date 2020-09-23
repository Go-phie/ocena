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

```bash
  pip install -r requirements.txt

  uvicorn main:app --debug
```

Visit http://localhost:8000/docs to interact with API
