# proleg

Aplicação Django que reúne informações sobre o processo legislativo na Câmara dos Deputados.

## Requisitos

- Python 3.13
- Django 5
- [DadosAbertosBrasil](https://pypi.org/project/DadosAbertosBrasil/) – dados públicos da Câmara
- Pillow

Instale as dependências com:

```bash
pip install django DadosAbertosBrasil Pillow
```

## Migrações

Crie ou atualize o banco de dados local executando:

```bash
python manage.py makemigrations
python manage.py migrate
```

## Testes

Para garantir que tudo está funcionando, execute:

```bash
python manage.py test
```

---

Projeto em desenvolvimento.
