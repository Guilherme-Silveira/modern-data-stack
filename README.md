# Modern Data Stack - K8S

Esse repositório tem como propósito criar uma Modern Data Stack do zero no Kubernetes. As ferramentas utilizadas nesse projeto são:

- Minio (Data Lake)
- Airflow (Orquestrador)
- Airbyte (EL(T))
- Hive Metastore (Metadados - Tabelas)
- Trino (Virtualizacão de dados - SQL)
- Superset (Data Viz)
- Trino + Minio (Data Lakehouse)

![architecture-mds](https://user-images.githubusercontent.com/40548889/206874592-3e6a2fd3-cf53-45dd-bcde-be3783717e74.png)


Todo esse ambiente foi criado em um cluster Kubernetes local na minha máquina pessoal utilizando o K3D, que utiliza o Docker para simular um cluster Kubernetes multi-node rodando em containers. Porém, todos os manifestos e helm charts criados nesse repositório podem ser utilizados em servicos gerenciados de Kubernetes de Cloud Providers (EKS, GKE, AKS), os únicos pré-requisitos seriam os seguintes:
- [Ingress Controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) configurado
- [Storage Class](https://kubernetes.io/docs/concepts/storage/storage-classes/) configurado

Nesse tutorial, todo o ambiente será criado utilizando o K3D para rodar em uma máquina local.

Pré-Requisitos:
- [Docker](https://www.docker.com/products/docker-desktop/) (No meu caso, o meu PC é um mac, mas você pode baixar a versão correspondente do seu Sistema Operacional)

OBS: o ambiente pode ser um pouco pesado, então em alguns casos será necessário mudar os valores de memória default dos manifests/helm charts.

Após a instalacão do Docker, teremos o necessário para configurar nosso ambiente big data, então bora para o tutorial!

---
# K3D
Para instalar o K3D, execute um dos comandos abaixo:
-  `wget -q -O - https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash`
-  `curl -s https://raw.githubusercontent.com/k3d-io/k3d/main/install.sh | bash`

Após instalado, já podemos criar um cluster. Para criar um cluster Kubernetes usando o K3D, execute o seguinte comando:
```
k3d cluster create --agents 3 -p '80:30000'
```
Ele criará um cluster Kubernetes com 1 master e 3 worker nodes. Lembrando que você pode colocar a qualquer quantidade de worker nodes, mas nesse tutorial, vamos seguir com 3.

Quando o K3D é instalado ele automaticamente instala o `kubectl` junto, então após o comando de criacão do cluster, você pode confirmar se tudo aconteceu conforme o esperado executando o seguinte comando:
```
kubectl get nodes
```

OBS: Esse Bind da porta 80 para a 30000 do cluster Kubernetes criado no Docker será explicado no próximo tópico.

---
# Ingress Controller
O Ingress Controller é um componente que permite o acesso externo a pods que estão executando dentro do Kubernetes. Em outras palavras, o Ingress Controller será nossa porta de acesso ao cluster.
Mas espera aí, é possível utilizá-lo em um ambiente rodando em uma máquina local?

Sim, é possível! Não é um método muito "elegante", mas é muito útil para o dia a dia. O mais interessante é que tudo que for aplicado nesse ambiente local, seria praticamente da mesma em um Cloud Provider. A única diferenca é que o Cloud Provider criaria um Load Balancer e Zonas DNS e aqui, nós utilizaremos o redirecionamento de porta do Docker e o arquivos Hosts da máquina local, mas a nível usuário e manisfestos, eles serão exatamente os mesmos.

Nesse tutorial, utilizaremos o Nginx como nosso Ingress Controller. Para criá-lo, a partir do diretório raiz do projeto, execute os seguintes comandos:
```
cd ingress-controller
kubectl apply -f ingress-controller.yaml
```
Dentro desse manifest, o Service do Nginx foi configurado como NodePort, tendo como bind a porta 30000 e aqui está a mágica de como tudo isso vai permitir acessos externos ao servicos do cluster.

No passo anterior, na criacao do cluster, definimos que toda requisicão feita na porta 80 da máquina local terá seu tráfego redirecionado para a porta 30000 do cluster Kubernetes que está executando dentro do Docker e agora, configuramos que o servico que está rodando nessa porta dentro do cluster Kubernetes será o Nginx, ou seja, o acesso externo terá o seguinte fluxo:

![network_flow](https://user-images.githubusercontent.com/40548889/170897468-e252bd8a-db5a-41d4-8190-cbd1102d9c74.png)

---
# Arquivo Hosts
O arquivo hosts da sua máquina permite que você adicione uma relacão de IP's e "registros DNS" que sua máquina irá traduzir para estabelecer uma comunicacão. 
Se você quiser utilizar os valores padrões que foram definidos nesse projeto, execute os seguintes passos:
```
sudo vim /etc/hosts
```
Adicione o seguinte conteúdo ao arquivo:
```
127.0.0.1 minio.silveira.com
127.0.0.1 console-minio.silveira.com
127.0.0.1 trino.silveira.com
127.0.0.1 superset.silveira.com
127.0.0.1 airflow.silveira.com
127.0.0.1 airbyte.silveira.com
```

Lembrando que é possível usar seu próprios "registros DNS" customizados, mas se esse for o caso, lembre-se de mudar os valores necessários nos manifests/helm charts durante o deploy de cada uma das ferramentas da stack.

---
# Namespace
No intuito de organizar, todo esse projeto vai ser criado em uma namespace específica do Kubernetes chamada bigdata.
Para criá-la, execute o seguinte comando no diretório raiz do projeto:
```
kubectl create namespace mds
```

---
# Minio
O [Minio](https://min.io/) é um Object Storage nativo para Kubernetes. O fato curioso é que ele utiliza o protocolo S3 para comunicacão, então é quase que uma solucão de S3 on-premises. Ele será o nosso Data Lake, onde todos os dados serão armazenados. 
Ele possui dois métodos principais de instalacão:
- Helm Chart
- Operator

Nesse tutorial, instalaremos o Minio via Helm Chart.

Para instalá-lo, a partir do diretório raiz do projeto, execute os seguintes comandos:
```
cd minio
bash install-minio.sh
```
Esse script simplesmente faz o download do repositório do Helm do Minio e instala-o utilizando como paramêtro o arquivo values.yaml que está dentro do diretório. Nesse arquivo são definidas todas as propriedades que Minio vai possuir (memória, storage, quantidade de nodes). Os valores default podem não atender exatamente o seu caso de uso, então sinta-se livre para modificar esse arquivo conforme sua necessidade.

Para validar que tudo ocorreu de acordo com o previsto, você pode acessar, no seu navegador, a console do Minio na seguinte URL:

`http://console-minio.silveira.com` 

O usuário e senha serão os seguintes, respectivamente:
- silveira
- guilherme@123


### OBS: O values.yaml será utilizado para todas as ferramentas que forem instaladas via Helm, então sinta-se livre para modificar as configuracões desse arquivo de acordo com seu caso de uso para qualquer ferramenta que o utilizar, por exemplo:
- ingress host (DNS)
- usuario
- senha
---
# Hive Metastore
O Hive Metastore não está descrito na arquitetura, mas é um componente importantíssimo para todo esse ambiente Big Data. O Hive Metastore é responsável por armazenar todos os metadados de tabelas que forem criadas via Spark e Trino. Ele necessita de um banco de dados relacional para armazenar esses metadados, então além do Hive Metastore, um deploy do MariaDB também será realizado. Para instalar o Hive Metastore, a partir do diretório raiz do projeto, execute os comandos abaixo:
```
cd hive-metastore
bash create-configmap.sh
kubectl apply -f maria_pvc.yaml
kubectl apply -f maria_deployment.yaml
kubectl apply -f hive-initschema.yaml
kubectl apply -f metastore.yaml
```
---
OBS: Caso o usuário e senha do Minio tenham sido alterados no passo anterior, será necessário executar os seguintes passos a partir do diretório raiz do projeto:
```
cd hive-metastore/build
vim core-site.xml
```
Modifique os seguintes paramêtros no arquivo para os valores configurados no Minio:
```
<property>
    <name>fs.s3a.awsAccessKeyId</name>
    <value>silveira</value>
</property>

<property>
    <name>fs.s3a.awsSecretAccessKey</name>
    <value>guilherme@123</value>
</property>
```
Salve o arquivo e agora execute os comandos:
```
cd ..
bash create-configmap.sh
```
Após isso, execute os comandos usando `kubectl` descritos no ínicio desse tópico.

---
# Airbyte
O Airbyte é uma ferramenta de EL(T), que a partir de uma interface simples e intuitiva, permite fazer a ingestão de dados de diversas fontes diferentes.
Para instalá-lo, a partir do diretório raiz do projeto, execute os seguintes comandos:
```
cd airbyte
bash install-airbyte.sh
```
Se os valores utilizados de ingress forem os defaults configurados nesse repositório, tente acessar no seu navegador a seguinte URL para validar se o Trino está funcionando:

`http://airbyte.silveira.com`

Caso não sejam os valores default, use a URL customizada que foi definida.

Seu funcionamento é muito simples. Todas as ingestões devem ser feitas na UI (super interativa por sinal), definindo `sources` e `destinations`. Depois de definir ambos, será necessário conectar ambos, para isso é necessário criar uma `connection` (defina o trigger da connection como `manual`, pois quem a executará será o Airflow). Feito o isso o Airbyte vai "coletar" os dados do `source` e enviar para a `destination`.

OBS: Para rodar essa connection no Airflow mais adiante, será necessário o ID da connection. Para isso, na UI, clique na connection criada. O seu ID será mostrado na URL como no exemplo abaixo:


No caso desse exemplo, o ID da connection é: `110a8c4a-b973-4c94-aeb8-0c0d5e5573b0`

---
# DBT (Data Build Tool)
O DBT é uma ferramenta de transformação de dados. Ela permite a criação de pipelines de transformação utilizando a Linguagem SQL. O DBT utiliza o poder de processamento do Data Warehouse/Lakehouse no qual está conectado para executar todas as suas tarefas.

Nesse ambiente, as pipelines do DBT (models) serão executadas pelo Airflow (semelhante ao SparkOnK8s Operator). Para que isso seja possível, para todo projeto de DBT, uma imagem Docker será criada com todo o projeto e o Airflow a executurá utilizando o KubernetesPodOperator.

Para criar a imagem, siga os seguintes passos (nesse projeto tem uma imagem de exemplo, mas os steps serão os mesmos para qualquer outro projeto):

- Crie a imagem base do DBT, utilizando o Adapter do Data Warehouse/Lakehouse que será utilizado. No nosso caso, será o Trino, então para criar a imagem, eu usei como base um Dockerfile fornecido pela própria DBT.
```
$ cd dbt/build-dbt-trino
$ docker build --tag guisilveira/dbt-trino \
  --target dbt-third-party \
  --build-arg dbt_third_party=dbt-trino \
  --build-arg dbt_core_ref=dbt-core@1.2.latest \
  .
```
- Crie o seu projeto DBT. Eu usei o exemplo fornecido pela própria DBT, mas fique a vontade para criar o seu. Nesse caso, eu criei o mesmo projeto duas vezes, porém com uma pequena diferença, a tabela final em um deles será criada no formato Delta e a outra no formato Iceberg (esse ambiente suporta ambas tecnologias, então escolha a que mais sentido para o seu use case, nesse exemplo, vou mostrar os comandos simulando o uso do Iceberg)
```
Instale o dbt-core na sua máquina local ou use uma imagem docker com um volume montado apontando para um diretório local e execute o seguinte comando

$ dbt init jaffle_shop_iceberg
```

- Modifique os arquivos dbt_project.yml e crie seus models no diretório models de acordo com seu use case (ou simplesmente use o exemplo que já está pronto)

- Crie o arquivo profiles.yml (no nosso caso, profiles_iceberg.yml). Esse arquivo vai definir as configurações necessárias para conectar o DBT ao Trino
``` yml
jaffle_shop:
  target: dev
  outputs:
    dev:
      type: trino
      user: trino
      host: tcb-trino
      port: 8080
      catalog: iceberg
      schema: transformed
      threads: 8
      http_scheme: http
      session_properties:
        query_max_run_time: 4h
        exchange_compression: True
```
- Após essas etapas, crie a imagem Docker que será executada pelo Airflow, usando a nossa imagem do dbt-trino que foi criada anteriormente como base (Dockerfile-iceberg):
``` Dockerfile
FROM guisilveira/dbt-trino

COPY ./jaffle_shop_iceberg/ /usr/app/

COPY ./profiles_iceberg.yml /root/.dbt/profiles.yml

CMD [ "run" ]
```
```
$ docker build -t guisilveira/dbt-jaffle-shop-iceberg -f ./Dockerfile-iceberg .
$ docker push guisilveira/dbt-jaffle-shop-iceberg
```

OBS: eu estou utilizando o repo `guisilveira` nas minhas imagens Docker pois é meu repo pessoal, mas no ambiente de vocês, mude para o seu repo pessoal/enterprise.

No diretório `examples` desse repo, haverá uma dag de exemplo que fará a ingestão usando o Airbyte e usa essa imagem que acabamos de criar para processar os dados utilizando o DBT

---
# Trino
O Trino é uma ferramenta de virtualizacão de dados que usa a linguagem SQL para interagir com diversas fontes de dados. Nesse tutorial, o Trino vai estar configurado com o Hive Metastore, Delta e Iceberg para se interagir com os dados armazenados no Minio.
Para instalá-lo, a partir do diretório raiz do projeto, execute os seguintes comandos:
```
cd trino
bash install-trino.sh
```
Se os valores utilizados de ingress forem os defaults configurados nesse repositório, tente acessar no seu navegador a seguinte URL para validar se o Trino está funcionando:

`http://trino.silveira.com`

Caso não sejam os valores default, use a URL customizada que foi definida.

Obs: Caso você não esteja utilizando o usuário e senha padrões definidos nesse tutorial para o Minio, você deve modificar os parâmetros de Access Key e Secret Key dentro do arquivo values.yaml para os conectores do Hive Metastore e do Delta Lake.

Há um exemplo no diretório `examples` desse repo com todas as tabelas que precisam ser criadas no Trino para que seja possível a execução do Job no DBT com o exemplo fornecido do Jaffle Shop.

Credenciais:
- Usuário: trino

---
# Airflow
O Apache Airflow é uma ferramenta de orquestracão de jobs muito usado no contexto de pipelines de ingestão Big Data. 

Um ponto importante sobre o airflow, é que todas as suas pipelines (chamadas de DAG's) são armazenadas em um repositório, utilizando a sincronizacão com o Git.
Para vincular as DAG's do Airflow ao seu repositório corporativo/pessoal, executa os seguintes passos:

Abra o arquivo values.yaml
```
cd airflow
vim values.yaml
```
Modifique os paramêtros `dags.gitSync` para os paramêtros desejados:
```
enabled: true
repo: https://github.com/Guilherme-Silveira/airflow-dags.git
branch: main
rev: HEAD
depth: 1
maxFailures: 0
subPath: "dags"
credentialsSecret: git-credentials
```

É importante notar que o paramêtro `credentialsSecret: git-credentials` faz referência a uma Secret que deve ser criada com suas credenciais de acesso ao repositório. Para fazer isso, execute os seguintes passos:

Crie um arquivo chamado `git-secret.yaml` com o seguinte conteúdo:
```
apiVersion: v1
kind: Secret
metadata:
  name: git-credentials
  namespace: bigdata
data:
  GIT_SYNC_USERNAME: <base64_encoded_git_username>
  GIT_SYNC_PASSWORD: <base64_encoded_git_password>
```

Após isso, execute o seguinte comando para criar a Secret:

```
kubectl apply -f git-secret.yaml
```

Para concluir a instalacão do Airflow, execute os seguintes comandos:
```
bash install-airflow.sh
```

Se os valores utilizados de ingress forem os defaults configurados nesse repositório, tente acessar no seu navegador a seguinte URL para validar se o Airflow está funcionando:

`http://airflow.silveira.com`

Caso não sejam os valores default, use a URL customizada que foi definida.

Há um exemplo no diretório `examples` desse repo em como construir uma dag chamando as connections do Airbyte e executando um Pod no Kubernetes com o seu projeto DBT.

Credenciais: 
  - Usuário: admin
  - Senha: admin

---
# Superset
O Apache Superset é uma ferramenta de visualizacão de dados. Para instalá-la, a partir do diretório raiz, execute os seguintes comandos:
```
cd superset
bash install-superset.sh
```

Se os valores utilizados de ingress forem os defaults configurados nesse repositório, tente acessar no seu navegador a seguinte URL para validar se o Superset está funcionando:

`http://superset.silveira.com`

Caso não sejam os valores default, use a URL customizada que foi definida.

Credenciais:
  - Usuário: admin
  - Senha: admin

---

Após todos esses procedimentos, sua Modern Data Stack estará funcionando! Espero que isso possa ser útil para vocês! Qualquer sugestão ou crítica construtiva, só avisar!
