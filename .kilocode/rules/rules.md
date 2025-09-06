Nesse projeto usamos o uv, logo para instalar um pacote usamos o comando:
```sh
uv add <pacote>
```
se o pacote for uma dependência de desenvolvimento, usamos:
```sh
uv add --dev <pacote>
```
Sempre pergunte se quero testes. Esse projeto é orientado a testes, logo  pois as funcionalidades novas podem ser acompanhadas de testes e testadas com o modo de Test Engineer.
Os testes devem ser sem dados mockados ou fictícios