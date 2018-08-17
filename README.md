# Curso Quant

## O que é um quant

Uma definição ampla de Quant


by Mark Joshi

Um quant projeta e implementa modelos matemáticos para o
precificação de ativos, avaliação de risco e previsão de movimentos de mercado.


Um modelo matemático é uma fórmula, equação, grupo de equações,
ou algoritmo computacional que tenta explicar algum tipo
de relação entre variáveis.


Os script deste repositório terão como foco primário a abordagem Quant
para a previsão de movimentos de mercado! Para isto fica uma definiçao
mais restrita de Ernie Chan

Um Quant realiza a compra e venda de ativos baseada estritamente em decisões de
um algoritmo de computador. Algoritmos estes desenvolvidos baseados em dados
históricos ou relações muito claras entre ativos.

Quant trade é a mesma coisa que trade técnico? Uma estratégia baseada em análise técnica
pode ser parte de um sistema de trade por algoritmos. Entretanto, nem todos métodos de
análise técnica podem ser transportados para o mundo quant. O mundo quantitativo aceita
apenas modelos sem subjetividade e que podem ser transformados em números.


## Insights Quants


https://quantocracy.com/  Mashup - Reune diversos artigos de fontes variadas do mundo quant

http://www.quantatrisk.com/  Conteúdo bem variado, de portfolio theory, análise de risco e backtest de estratégias simples com bastante uso de Python

http://www.epchan.blogspot.com  Blog do Ernie Chan, uma das primeiras referências como trader Quant, com bastante foco em arbitragem estatística

https://www.ssrn.com/  Para abordagens acadêmicas, é uma boa fonte de artigos

https://www.quantstart.com/

## Exemplos Clássicos de Estratégias Quantitativas

Trend Following - modelo de operação de tendências

Pairs Trading - arbitragem estatística, baseada na relaçao estatística em pares de ações

Arbitragem - comprar e venda de um mesmo ativo em mercados diferentes sendo a venda num preços mais altos que a compra
    ex.: Arbitragem cheio x mini, arbitragem entre a ação de uma empresa brasileira contra a ADR, arbitragem triangular de moedas,
         arbitragem em curva de juros, arbitragem futuro x spot,

Market making



## BASE DE DADOS

Existem muitas razões pelas quais você deve criar seu próprio banco de dados. Você tem
seus dados sempre acessíveis e é capaz de realizar backtests. O package Arctic para Python
desenvolvido pela Man AHL fornece tudo o que precisamos para nossos propósitos. O Arctic é uma datastore
de alto desempenho para dados numéricos. Ele suporta Pandas, numpy arrays e objetos picklados e suporte
para outros tipos de dados. Ele pode fazer o query de milhões de linhas por segundo por cliente. É uma
datastore desenvolvida para no mercado financeiro capaz de lidar com dados de tick de modo eficiente.



**Passo a passo para criar a base de dados**

`1)` Instalar o MongoDB

O Arctic utiliza o MongoDB como Database, por isso, antes de comecar é necessário
instalar o mongoDB no computador

Site para download: https://www.mongodb.com/download-center#community
Tutorial de instalação: https://docs.mongodb.com/manual/tutorial/

Basicamente após a instalação no Windows você terá de criar uma pasta onde ficará
armazenada a base de dados. Ex.: d:\test\mongo

Após é só inicializar o mongo via cmd com o seguinte codigo:
"C:\Program Files\MongoDB\Server\4.0\bin\mongod.exe" --dbpath="c:\data\db"
Sugiro a criação de um arquivo .bat que ao inicializado roda automaticamente o código acima.


`2)` Instalar o Arctic

Para instalar o arctic basta rodar o comando

pip install git+https://github.com/manahl/arctic.git

O github tem todo o material básico de como usar o arctic e vale uma lida:
https://github.com/manahl/arctic


`3)` Import de dados

O Arctic suporta a importação de pandas Dataframe, o que facilita a vida de um
analista de dados.

**Caso não saiba usar a biblioteca pandas do python vale a pena dar uma
lida nos tutoriais que o próprio pandas fornece. É todo desenvolvido em
jupyter notebooks e com vários exemplos de código >> https://pandas.pydata.org/pandas-docs/stable/tutorials.html**

O codigo arctic_basics.py ensina como utilizar o Arcitic para organizar os seus dados


`4)` Encontrar uma boa fonte de dados

Existem diversas fontes de dados de mercado financeiro gratuitas na internet de qualidade que podem
ser úteis para analistas quant. Cito como exemplo o Yahoo Finance, Quandl e google
finance. Todos possuem api's para python e dados de diversos mercados.
Para o mercado brasileiro, a B3 fornece dados via ftp. Aí fica armazenada toda mensageria
BM&F e Bovespa para os últimos dois anos. São dados pesados, com todas mensagens de trade e
book para derivativos, ações e opções que valem a pena serem analisados.

**Os arquivos na pasta BMFData criam uASE DE DADOSma base de dados a partir do ftp da B3, tanto para
derivativos quanto para ações**



## BACKTESTING

O que é? Testar modelos pré definidos em uma base de dados históricas.
Fazer simulação de operações

Para realizar um backtest é necessário uma base de dados confiável. Um bom conhecimento
em pandas tornará o backtest ágil. Os Scripts da pasta backtesting são exemplos
de como realizar um backtest

As métricas mais utilizadas para analisar o backtest são sharpe ratio, drawdown, retorno médio por trade

Cuidado com o survivorship bias e data-snooping bias

Qual o capacity estimado da sua estratégia?

O script 1 - Faz um backtest de uma simples estratégia de reversão a média para a ação ABEV3
O script 2 - Faz o mesmo backtest mas para um conjunto de ações e calcula sharpe, drawdown, retorno absoluto
O script 3 - Faz uma análise de sensibilidade a parâmetros da mesma estratégia
O script 4 - Mostra como se faz uma análise de contegração
O script 5 - Faz um backtest inicial de pairs trading com cointegração



## RISCO

O script var_risco calcula o VaR de posições em ações dado a metodologua riskMetrics, muito utilizada no mercado
Entreatanto, há outras formas diferentes que complemantam a gestão de risco, como o cálculo de stress, o cálculo de
exposição, o var histórico, entre outros.
