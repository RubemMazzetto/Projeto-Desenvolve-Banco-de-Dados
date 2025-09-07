Zé Delivery Backend Challenge
API REST para o desafio de backend do Zé Delivery, implementada em Python com FastAPI e MySQL (com PostGIS).
Pré-requisitos

Docker e Docker Compose
Python 3.9+
MySQL 8.0 com extensão PostGIS

Configuração

Clone o repositório:
git clone <seu-repositorio>
cd <seu-repositorio>


Configure o banco de dados:

Inicie o MySQL com PostGIS usando Docker:docker-compose up -d


O arquivo docker-compose.yml está configurado para criar um banco ze_delivery com usuário user e senha password.


Instale as dependências:
pip install -r requirements.txt


Rode a aplicação:
uvicorn main:app --host 0.0.0.0 --port 8000



Endpoints

POST /partners: Cria um parceiro.
Exemplo de body:{
  "tradingName": "Loja Exemplo",
  "ownerName": "João Silva",
  "document": "12345678901",
  "coverageArea": {
    "type": "MultiPolygon",
    "coordinates": [[[[-46.6, -23.5], [-46.6, -23.6], [-46.5, -23.6], [-46.5, -23.5], [-46.6, -23.5]]]]
  },
  "address": {
    "type": "Point",
    "coordinates": [-46.55, -23.55]
  }
}




GET /partners/{id}: Retorna um parceiro pelo ID.
GET /partners/search?lat={lat}&long={long}: Retorna o parceiro mais próximo cuja área de cobertura contém o ponto.

Testando

Acesse a documentação interativa em http://localhost:8000/docs.
Use ferramentas como Postman ou cURL para testar os endpoints.

Estrutura do Projeto

main.py: Código principal da API.
requirements.txt: Dependências do Python.
docker-compose.yml: Configuração do MySQL com PostGIS.

Notas

O MySQL com PostGIS é usado para suportar consultas geoespaciais (ST_Contains e ST_Distance).
GeoJSON é validado usando a biblioteca geojson.
A unicidade de id e document é garantida pelo banco.
