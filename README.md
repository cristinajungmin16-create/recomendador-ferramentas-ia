# recomendador-ferramentas-ia
Sistema de recomendar ferramentas de inteligencia artificial usando crisp-dm

## 1. Objetivo

Desenvolver um sistema de recomendação de ferramentas de inteligência artificial que auxilie usuários a identificar soluções compatíveis com suas necessidades, considerando modalidade, categoria e características técnicas.

**Aplicativo:** https://recomendador-ferramentas-ia-poedu7nobgs6zvtnjdytpb.streamlit.app/

## 2. Base de dados

O projeto utiliza um catálogo de 113 ferramentas de inteligência artificial, obtido do dataset `tarekmasryo/genai-tools-platforms-data`, disponível no Hugging Face.

As informações incluem nome, empresa, categoria, modalidade principal, disponibilidade de API e código aberto.

A base foi preparada e enriquecida com informações adicionais sobre funcionalidades de ferramentas de programação.

## 3. Metodologia

Foram implementados e comparados dois métodos de recomendação baseados em conteúdo:

**Ranking ponderado:** atribui pontuações conforme a compatibilidade entre as características da ferramenta e as preferências informadas pelo usuário.

**Similaridade de cosseno:** calcula a similaridade entre o perfil da consulta e a representação das características das ferramentas.

O aplicativo incorpora filtros e critérios adicionais para personalizar as recomendações.

## 4. Avaliação

Os métodos foram avaliados utilizando 12 consultas representativas de diferentes necessidades.

| Método | Precision@5 médio |
|---|---|
| Ranking ponderado | 90% |
| Similaridade de cosseno | 90% |

Os dois métodos produziram recomendações idênticas nas consultas avaliadas.

**Limitações:** a avaliação é exploratória, baseada em um conjunto reduzido de consultas e julgamentos de relevância parcialmente preliminares. Os resultados não representam uma estimativa independente da precisão do aplicativo em uso real.

## 5. Tecnologias

- Python
- Pandas
- Scikit-learn
- Jupyter Notebook
- Streamlit
- GitHub

## 6. Como executar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Execute o aplicativo:

```bash
streamlit run app.py
```

## 7. Limitações e melhorias futuras

O catálogo contém informações limitadas sobre funcionalidades específicas das ferramentas.

Entre as melhorias futuras estão a ampliação da base de dados, a validação independente das recomendações, o enriquecimento das capacidades funcionais e a avaliação com um conjunto maior de consultas.

## 8. Aplicativo

Acesse o recomendador:

https://recomendador-ferramentas-ia-poedu7nobgs6zvtnjdytpb.streamlit.app/
