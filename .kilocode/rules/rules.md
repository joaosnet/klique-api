Sempre usamos o mcp do context7 para usarmos o contexto da bibliotecas antes de fazer qualquer implementação.
Nesse projeto usamos o uv, logo para instalar um pacote usamos o comando:
```sh
uv add <pacote>
```
se o pacote for uma dependência de desenvolvimento, usamos:
```sh
uv add --dev <pacote>
```
Esse projetos é orientado a testes, logo todas as funcionalidades novas devem ser acompanhadas de testes e testadas com o modo de Test Engineer.
