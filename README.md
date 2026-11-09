# Ponte Alimentar SP

Aplicação em Python desenvolvida para a **Global Solution 2026.2 da FIAP (tema CitizenTech)**, na disciplina **Computational Thinking with Python**.

## Descrição da CitizenTech

A Ponte Alimentar SP conecta estabelecimentos que têm **alimentos excedentes** (feiras, padarias, restaurantes e mercados) a **ONGs e cozinhas comunitárias** de São Paulo. O sistema avalia a urgência de cada doação pelo tempo restante até a validade e sugere automaticamente a ONG mais compatível para recebê-la.

## Problema identificado

Muitos alimentos ainda próprios para consumo são descartados todos os dias, enquanto instituições que atendem pessoas em situação de vulnerabilidade precisam de doações. Falta coordenação: quem tem a sobra não sabe, a tempo, quem pode recebê-la, e alimentos perecíveis acabam vencendo antes de chegar a alguém.

## Público beneficiado

- **Famílias e pessoas atendidas** por ONGs e cozinhas comunitárias, que recebem mais alimentos.
- **ONGs**, que passam a receber doações compatíveis com sua estrutura (categoria, refrigeração e capacidade).
- **Estabelecimentos doadores**, que reduzem o descarte de alimentos.

ODS relacionados: **ODS 2 (Fome Zero)** e **ODS 12, meta 12.3 (reduzir pela metade o desperdício de alimentos)**.

## Objetivo da aplicação

Processar as informações de doações e ONGs para **decidir qual doação é mais urgente** e **qual ONG deve recebê-la**, acompanhando cada doação até a entrega e medindo o impacto em quilos de alimento aproveitado.

## Principais funcionalidades

| Opção | Funcionalidade |
|---|---|
| 1 | Cadastrar ONG (região, categorias aceitas, refrigeração e capacidade) |
| 2 | Listar ONGs com a capacidade disponível |
| 3 | Cadastrar doação (doador, alimento, categoria, quantidade, região e validade) |
| 4 | Listar doações ativas ordenadas por urgência, e as doações encerradas |
| 5 | Encontrar as ONGs compatíveis com uma doação e reservar |
| 6 | Confirmar a entrega de uma doação reservada |
| 7 | Relatório de impacto (kg entregues, kg perdidos e taxa de aproveitamento) |
| 0 | Sair |

### Regras de negócio

| Regra | Descrição |
|---|---|
| RN01 | Nenhum campo pode ficar vazio |
| RN02 | A quantidade de uma doação deve estar entre 0,1 e 1000 kg |
| RN03 | A validade deve estar no formato dd/mm/aaaa hh:mm e no futuro |
| RN04 | Urgência: até 6h **CRÍTICA**, até 24h **ALTA**, até 72h **MÉDIA**, acima disso **BAIXA** |
| RN05 | Alimentos perecíveis e preparados só vão para ONGs com refrigeração |
| RN06 | A ONG precisa aceitar a categoria e ter capacidade disponível para a quantidade |
| RN07 | Ordem de sugestão: ONGs da mesma região primeiro; depois, as de maior capacidade disponível |
| RN08 | Doações disponíveis ou reservadas que passam da validade são marcadas como **expiradas** automaticamente |
| RN09 | Somente doações reservadas podem ser entregues; entregues e expiradas não mudam mais de status |
| RN10 | Na entrega, a quantidade é somada ao total recebido pela ONG |
| RN11 | Os ids são gerados automaticamente, em sequência |

## Tecnologias utilizadas

- **Python 3.10 ou superior**: necessário por causa do `match/case`. O projeto foi executado com Python 3.14.
- Módulos da biblioteca padrão do Python (não precisam de instalação):
  - `json`: leitura e gravação dos dados;
  - `datetime`: cálculo do tempo restante até a validade.
- Nenhuma biblioteca externa.

## Como executar o programa

1. Instale o Python 3.10 ou superior.
2. Abra um terminal **dentro da pasta do projeto** (a pasta onde está o `main.py`).
3. Execute:

```
python main.py
```

4. Navegue pelo menu digitando o número da opção desejada.

O caminho do arquivo de dados (`dados/dados.json`) é relativo. Por isso, o programa deve ser executado a partir da pasta do projeto.

## Como os dados são armazenados

Os dados ficam no arquivo `dados/dados.json`, que é carregado quando o programa abre e salvo a cada alteração (cadastro, reserva, entrega ou expiração). O arquivo tem duas listas, `ongs` e `doacoes`:

```json
{
  "ongs": [
    {
      "id": 1,
      "nome": "Cozinha Solidária Leste",
      "regiao": "Leste",
      "categorias_aceitas": ["perecível", "não perecível", "preparado"],
      "refrigeracao": true,
      "capacidade_kg": 200.0,
      "recebido_kg": 40.0
    }
  ],
  "doacoes": [
    {
      "id": 1,
      "doador": "Padaria Bom Pão",
      "alimento": "Pães variados",
      "categoria": "não perecível",
      "quantidade_kg": 12.0,
      "regiao": "Leste",
      "validade": "12/11/2026 18:00",
      "status": "disponível",
      "ong_id": null
    }
  ]
}
```

- `status` pode ser: `disponível`, `reservada`, `entregue` ou `expirada`.
- `ong_id` guarda o id da ONG que reservou a doação (`null` enquanto ela não for reservada).

Tratamento de erros do arquivo:

- **Arquivo inexistente:** o sistema avisa e inicia sem registros. O arquivo é criado no primeiro cadastro.
- **Arquivo corrompido:** o sistema avisa e inicia sem registros. Atenção: o próximo salvamento substitui o conteúdo antigo.
- **Falha ao gravar:** o sistema avisa o usuário e continua funcionando.

O arquivo enviado com o projeto já contém ONGs e doações de exemplo para demonstração. As datas de validade de exemplo podem precisar de ajuste para ficarem no futuro na data da apresentação.

## Integrantes

Gabriel Viana Cumino - RM571475

Guilherme Mingues Matos - RM568670

Murillo Padula de Gouveia RM571620

Renato Munhoz Mariana - RM573570