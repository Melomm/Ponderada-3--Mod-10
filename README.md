# API de figurinhas da Copa 2026

API REST para cadastrar, listar, buscar, atualizar e remover figurinhas de um álbum da Copa do Mundo 2026.

Montei o projeto com FastAPI, SQLite e uma separação simples em camadas. A ideia foi deixar claro onde cada parte existe e sua função: rota cuida de HTTP, service cuida das regras, repository cuida do banco e domain representa a figurinha.

## Arquitetura

A estrutura do projeto:

```text
internal/
├── database/
│   └── sqlite.py
├── domain/
│   └── figurinha.py
├── errors/
│   └── errors.py
├── handler/
│   └── http_handler.py
├── repository/
│   ├── figurinha_repository.py
│   └── sqlite_figurinha_repository.py
└── service/
    └── figurinha_service.py
```

O `domain` tem a entidade `Figurinha` e os valores aceitos para tipo e posição.

O `repository` concentra os comandos SQL. Isso evita espalhar consulta de banco pelo restante do código.

O `service` guarda as regras de negócio: campos obrigatórios, tipo permitido, posição permitida, datas automáticas e erro para figurinha inexistente.

O `handler` expõe as rotas com FastAPI e traduz os erros do domínio para respostas HTTP.

A injeção de dependência é feita manualmente em `main.py`:

```python
db = connect("figurinhas.db")
migrate(db)

repository = SQLiteFigurinhaRepository(db)
service = FigurinhaService(repository)
app = build_app(service)
```

## Tecnologias

- Python 3
- FastAPI
- Uvicorn
- SQLite
- Pydantic
- unittest

FastAPI funciona bem pois deixa as rotas limpas, gera documentação automática e facilita o trabalho com parâmetros de rota e query string.

SQLite foi suficiente tambem, o projeto precisa de um banco local simples então não faria muito sentido depender de um banco mais pesado só para demonstrar a arquitetura.

## Como Rodar

Instale as dependências:

```bash
pip install -r requirements.txt
```

Suba a API:

```bash
python main.py
```

Também dá para rodar direto com Uvicorn:

```bash
uvicorn main:app --host localhost --port 8080
```

A API fica disponível em:

```text
http://localhost:8080
```

A documentação interativa fica em:

```text
http://localhost:8080/docs
```

## Banco SQLite

O arquivo `figurinhas.db` é criado automaticamente na primeira execução.

A tabela também é criada automaticamente:

```sql
CREATE TABLE IF NOT EXISTS figurinhas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    numero TEXT NOT NULL,
    tipo TEXT NOT NULL,
    posicao TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
```

As datas são preenchidas pela aplicação. O cliente não deve enviar `id`, `created_at` ou `updated_at`.

## Valores Aceitos

Tipos:

```text
comum
brilhante
legends_ouro
legends_bronze
```

Posições:

```text
Goleiro
Zagueiro
Meio-campista
Atacante
```

## Endpoints

Os exemplos abaixo estão em PowerShell pois estou no windows :)

Usei `Invoke-RestMethod` pois no PowerShell o comando `curl` pode virar alias de `Invoke-WebRequest`.

### Criar Figurinha

```powershell
$body = @{
    numero = "BRA 15"
    tipo = "comum"
    posicao = "Atacante"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8080/figurinha" `
    -Method Post `
    -ContentType "application/json" `
    -Body $body
```

Resposta:

```http
HTTP/1.1 201 Created
```

```json
{
  "id": 1,
  "numero": "BRA 15",
  "tipo": "comum",
  "posicao": "Atacante",
  "created_at": "2026-06-03T14:30:00+00:00",
  "updated_at": "2026-06-03T14:30:00+00:00"
}
```

### Listar Figurinhas

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/figurinha" -Method Get
```

Com filtro por tipo:

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/figurinha?tipo=comum" -Method Get
```

Com filtro por posição:

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/figurinha?posicao=Atacante" -Method Get
```

Resposta:

```json
[
  {
    "id": 1,
    "numero": "BRA 15",
    "tipo": "comum",
    "posicao": "Atacante",
    "created_at": "2026-06-03T14:30:00+00:00",
    "updated_at": "2026-06-03T14:30:00+00:00"
  }
]
```

### Buscar por ID

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/figurinha/1" -Method Get
```

Quando não existe:

```http
HTTP/1.1 404 Not Found
```

```json
{
  "error": "figurinha não encontrada"
}
```

### Atualizar Figurinha

```powershell
$body = @{
    numero = "BRA 15"
    tipo = "brilhante"
    posicao = "Atacante"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://localhost:8080/figurinha/1" `
    -Method Put `
    -ContentType "application/json" `
    -Body $body
```

O `created_at` original é mantido e o `updated_at` é recalculado.

### Remover Figurinha

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/figurinha/1" -Method Delete
```

Resposta esperada:

```http
HTTP/1.1 204 No Content
```

## Exemplos de Erro

Campo obrigatório ausente:

```json
{
  "error": "campo obrigatório ausente: numero"
}
```

Tipo inválido:

```json
{
  "error": "tipo inválido. Use: comum, brilhante, legends_ouro ou legends_bronze"
}
```

Tentativa de enviar data controlada pela API:

```json
{
  "error": "o campo created_at é controlado pela API"
}
```

## Testes

```bash
python -m unittest discover -s tests
```

Os testes cobrem as regras do service: criação com datas automáticas, campos obrigatórios, tipo inválido, filtro por tipo e ID inexistente.

## Algumas outras decisões :D

Deixei as validações no service pois elas fazem parte da regra da figurinha, não da forma como a requisição chega. O Pydantic poderia validar mais coisas sozinho, mas isso jogaria uma parte meio importante da regra para dentro do handler.

O repositório retorna `None` quando não encontra uma figurinha. Quem transforma isso em `ErrFigureNotFound` é o service, esse erro faz parte do caso de uso.

No update usei `PUT` como substituição completa dos campos editáveis. Por isso `numero`, `tipo` e `posicao` seguem obrigatórios na atualização.

O formato dos erros de domínio é `{"error": "..."}`. FastAPI normalmente usa `detail`, mas o handler devolve `JSONResponse` para manter o retorno pedido.

## Indo Alem

### Abrir Pacotinho

```powershell
Invoke-RestMethod -Uri "http://localhost:8080/pacotinho" -Method Get
```

Esse endpoint cria uma figurinha aleatória e já salva no banco.

Resposta:

```json
{
  "mensagem": "Veio uma brilhante.",
  "figurinha": {
    "id": 1,
    "numero": "BRA 15",
    "tipo": "brilhante",
    "posicao": "Atacante",
    "created_at": "2026-06-03T14:30:00+00:00",
    "updated_at": "2026-06-03T14:30:00+00:00"
  }
}
```

O `/pacotinho` entrou como um pequeno extra. A geração aleatória e a mensagem ficam no service pois são regras do pacote. O repository continua só salvando e buscando dados no SQLite.
