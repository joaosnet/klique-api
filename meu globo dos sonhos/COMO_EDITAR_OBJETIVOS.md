# Como Editar os Objetivos do Mural

## Arquivo de Objetivos: `objetivos.json`

Para adicionar, remover ou editar os objetivos exibidos no mural, edite o arquivo **`objetivos.json`**.

### Estrutura de cada objetivo:

```json
{
  "title": "Título do objetivo",
  "image": "./images/nome-da-imagem.png",
  "x": -2.22,
  "y": -0.17,
  "z": 7.0,
  "tiltX": -0.07,
  "scale": 0.55,
  "rotation": -0.04
}
```

### Campos:

- **`title`**: Texto que aparece na legenda da Polaroid (suporta quebra automática de linha)
- **`image`**: Caminho da imagem (coloque as imagens na pasta `images/`)
- **`x`, `y`, `z`**: Posição esférica 3D da Polaroid colada no globo terrestre.
- **`scale`**: Escala que define o tamanho visual da Polaroid.
- **`tiltX`** e **`rotation`** (ou `tilt`): Inclinações individuais nos eixos tridimensionais da Polaroid colada na esfera.

### Exemplo - Adicionar novo objetivo:

```json
[
  {
    "title": "Meu Novo Objetivo",
    "image": "./images/novo-objetivo.png",
    "x": 0,
    "y": 0,
    "z": 5.0,
    "tiltX": -0.07,
    "scale": 0.85,
    "rotation": 0.1
  }
]
```

### Dicas:

1. **Imagens**: Use PNG ou JPG com boa resolução (recomendado: 800x800px ou maior)
2. **Títulos**: Textos longos quebram automaticamente em múltiplas linhas
3. **Posições**: Após carregar, você pode arrastar as Polaroids e usar o atalho **V** para exportar as posições finais
4. **Backup**: Sempre faça backup do arquivo antes de editar

### Exportar Layout:

Depois de ajustar manualmente o tamanho (`[` ou `]`), giro (`.` ou `,`) e drag (arraste livre ao redor do globo):

1. Pressione **V** no teclado
2. Abra o Console do navegador (F12)
3. Copie o JSON gigante que será ejetado lá com as fotos e as coordenadas em tempo real!
4. Cole por cima do arquivo **`objetivos.json`** e salve para que da próxima vez, a página recarregue exatamente daquele jeito.
