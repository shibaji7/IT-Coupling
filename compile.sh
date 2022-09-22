rm -rf `find -type d -name .ipynb_checkpoints`
rm -rf `find -type d -name __pycache__`

isort -rc -sl py/
autoflake --remove-all-unused-imports -i -r py/
isort -rc -m 3 py/
black py