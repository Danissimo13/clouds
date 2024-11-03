# Лабораторная работа 4
# CI/CD Build and Deploy

## Задание

1. Написать “плохой” CI/CD файл, который работает, но в нем есть не менее пяти плохих практик по написанию CI/CD
2. Написать “хороший” CI/CD, в котором все плохие практики исправлены
3. Указать, как были исправлены плохие практики на хорошие, сравнить полученный результат

## Ход работы

### Введение

В качестве CI/CD был выбран Github Actions, наверное самый простой для введения в CI/CD и позволяющий одновременно хранить свой CI/CD в моно-репозитории вместе с кодом и описанией инфрастуктуры.

Я написал CI/CD сразу в правильном виде, разбив на разные воркфлоу - билд, деплой, воркфлоу для разделения или совмещения билда и деплоя, и отдельный воркфлоу для финального ручного запуска процесса билда/деплоя.

Опишу bad practices, и как они исправлены в итоговом CI/CD.
Конечно написанный CI/CD получился не идеальный, там нет:
1. Прогона тестов
2. Автоматического билда при пуше в мастер (или в RC ветку)

Но зачастую данные параметры и не нужны для большинства проектов.

C CI/CD я работал и работаю время от времени на работе, и это как раз GitHub Actions, хотя я думал над внедрением другого инструментария, и даже поднимал его на стейдж окружении, например ArgoCD и Jenkins, однако для наших реалий это был очень большой оверхед, и нам пока с головой хватает GitHub Actions.

### Описание

#### Bad/Best Practices - как не надо делать, а как надо:
- Весь CI/CD пайплайн в одной джобе и в одном степе:
 Писать все комманды и шаги сборки/тестов/деплоя/пост-деплойных тестов в одной джобе и в одном степе конечно очень плохо, и причин несколько:
    1. Это невозможно читать и разбираться в этом
    2. Если что-то завалится придется бегать по логам и искать почему именно
    3. При необходимости пропускать какие-то комманды или добавлять новые, надо будет лепить условные конструкции на bash
    
- Плохое именование шагов и джоб:
  Как и в программировании, надо правильно именовать каждую вещь, что бы другой человек (или вы через год), смогли с легкостью разобраться и понять, что происходит в CI/CD и что делает каждый шаг и джоба

- Слияние билда и деплоя (и тестов):
  Разделять воркфлоу или хотя бы джобы билда, деплоя и тестов надо с самого начала, и это без сомнения рано или поздно понадобится, к тому же это предостерегает от ошибочных деплоев на прод сломанных билдов. Надо разделять все эти воркфлоу, и обьединять их в другом, что бы можно было условно собрать и задеплоить на тестовой окружение, а после ручных тестов уже запустить только деплой на прод - так у вас на прод попадет билд который уже был успешно протестирован на тестовом окружении. (к сожалению это не спасает от непроставленных секретов для прод окружения)

- Секреты в workflow:
  Так не надо, иначе любой кто увидит логи CI/CD - увидит и секреты, как минимум - Github Actions Secrets - очень удобный и легкий инструмент, зачастую его хватает. Но если очень надо защитить секреты, что, даже в yaml файлах кубера или в env машины на которой все будет работать, этих секретов не должно быть видно, то можно использовать Hashicorp Vault, с внедрением контейнера в под, сохранения файла с секретами, и удалением этого файла после чтения приложением (на работе я так сделал, но для нас это опять был очень большой оверхед).

- Реализация авто-запуска CI/CD для всех веток:
  Если у вас настроен автоматический запуск пайплайна, то надо явно указывать с каких веток этот пайплайн должен отслеживать пуши, что бы запускаться. Обычно такими ветками выступают RC (release candidate) ветки.

- Отсутствие разделения на окружения:
  Для CI/CD надо явно разделять окружения на которые производится деплой, например для тестового окружения можно пропустить тесты, а для прод окружения без них уже деплой запускать нельзя. К тому же это позволяет разделять секреты, а не скидывать все секреты для тестового и прод окружений на любое окружение.

### Что сделано
А сделан простой пайплан билда и деплоя серверного приложения на Yandex Cloud в кластер кубера. CI/CD сделан в качестве ручного запуска, без тестов, но с возможностью выбора действия (build/deploy/buildAndDeploy), выбора окружения (описан только dev), с использованием секретов.

Разберем по порядку, что будет если запустить CI/CD сервиса с Build And Deploy:
1. Входной файл, который запускается ручками:
```yml
name: "[Services] 🚀 Deploy Backend #1"
run-name: ${{ inputs.workflow-action }} on ${{ inputs.environment }} by @${{ github.actor }} from ${{ github.ref }}

on:
  workflow_dispatch:
    inputs:
      environment:
        description: Environment
        required: true
        type: choice
        options:
          - dev
          - staging
          - prod
      helm-action:
        type: choice
        description: Action
        options:
          - upgrade
          - install
          - lint
          - template
      workflow-action:
        type: choice
        description: Workflow Action
        options:
          - Build
          - Deploy
          - Build And Deploy
      clouds-integration:
        type: boolean
        description: Clouds Integration Service
      
jobs:
  clouds-integration:
    if: ${{ inputs.clouds-integration }}
    uses: ./.github/workflows/wfc-build-deploy-backend-service.yml
    with:
      helm-action: ${{inputs.helm-action}}
      service-name: clouds-integration
      dockerfile-path: ./Lab4/CloudsIntegration/CloudsIntegration/Dockerfile
      environment: ${{inputs.environment}}
      workflow-action: ${{inputs.workflow-action}}
    secrets: inherit
```
Итак, как можно видеть, пользователь может выбрать окружение, helm действие (обычно install или upgrade), действие которое надо сделать (build/deploy/buildAndDeploy), и дальше чек-боксами идут сервисы, которые надо обработать (тут он один). После запуска он вызывает для каждого сервиса workflow который перенаправит действия другим workflow.
2. Workflow который смотрит на действие и вызывает другие Workflow:
```yml
name: "[Z] Build and deploy backend .net service"

on:
  workflow_call:
    inputs:
      helm-action:
        required: true
        type: string
      service-name:
        required: true
        type: string
      dockerfile-path:
        required: true
        type: string
      workflow-action:
        required: true
        type: string
      environment:
        required: true
        type: string

jobs:
  build:
    if: ${{ inputs.workflow-action == 'Build' || inputs.workflow-action == 'Build And Deploy' }}
    uses: ./.github/workflows/wfc-build-image.yml
    with:
      environment: ${{inputs.environment}}
      dockerfile-path: ${{inputs.dockerfile-path}}
      registry-path: ${{inputs.service-name}}
    secrets: inherit

  deploy:
    if: ${{ inputs.workflow-action == 'Deploy' }}
    uses: ./.github/workflows/wfc-deploy-backend-service.yml
    with:
      environment: ${{inputs.environment}}
      helm-action: ${{inputs.helm-action}}
      service-name: ${{inputs.service-name}}
    secrets: inherit
          
  build_and_deploy:
    if: ${{ inputs.workflow-action == 'Build And Deploy' }}
    needs: [build]
    uses: ./.github/workflows/wfc-deploy-backend-service.yml
    with:
      environment: ${{inputs.environment}}
      helm-action: ${{inputs.helm-action}}
      service-name: ${{inputs.service-name}}
    secrets: inherit

```
Тут можно видеть, что он получает название сервиса, окружение, helm action, и дейсвтие которое надо совершить, после чего на основе этого действия - собирает образ/деплоит/собирает образ+деплоит наш сервис, и все это путем вызова двух оставшихся workflow которые отвечают за билд+пуш образа в регистр контейнеров и за деплой в кластер.
3. Билд образа и пуш в реестр
```yml
name: "[Z] Build .NET image"

on:
  workflow_call:
    inputs:
      dockerfile-path:
        required: true
        type: string
      registry-path:
        required: true
        type: string
      environment:
        required: true
        type: string

jobs:
  build-image:
    runs-on: ubuntu-latest
    steps:
      - name: Get commit info
        id: commit
        uses: prompt/actions-commit-hash@96297fd87f37de8995123eefa42cfe774416d8f1

      - name: Get Yandex token
        uses: yc-actions/yc-iam-token@v1
        id: yandex-cloud-iam-token
        with:
          yc-sa-json-credentials: ${{ secrets.YC_SA_DEV_JSON_CREDENTIALS }}
        
      - name: Docker login in registry
        uses: docker/login-action@v2.0.0
        with:
          registry: cr.yandex
          username: iam
          password: ${{ steps.yandex-cloud-iam-token.outputs.token }}

      - name: Build and push
        uses: docker/build-push-action@v3
        with:
          push: true
          no-cache: true
          tags: cr.yandex/crp76aifpa9n0b74vbhm/${{ inputs.registry-path }}:${{ steps.commit.outputs.short }}
          file: ${{ inputs.dockerfile-path }}
```
С этим workflow все просто, он получает путь к докерфайлу сервиса, путь реестра контейнеров и окружение, затем он достает хеш-коммита с которого запущен пайплайн, получает IAM токен яндекс облака для доступа в реестр контейнеров, собирает и пушит этот образ в реестр контейнеров.

4. Деплой
```yml
name: "[Z] Deploy backend .net service"

on:
  workflow_call:
    inputs:
      helm-action:
        required: true
        type: string
      service-name:
        required: true
        type: string
      environment:
        required: true
        type: string
        
jobs:
  deploy_dev:
    runs-on: ubuntu-latest
    if: ${{ inputs.environment == 'dev' }}
    steps:
      - uses: actions/checkout@master

      - name: Get commit info
        id: commit
        uses: prompt/actions-commit-hash@v3

      - name: Extract branch name
        shell: bash
        run: (echo "branch=${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}" | sed 's#/#\_#g') >> $GITHUB_OUTPUT
        id: extract_branch

      - name: Deploy service to cluster
        uses: wahyd4/kubectl-helm-action@master
        env:
          KUBE_CONFIG_DATA: ${{ secrets.KUBE_DEV_CONFIG_DATA }}
        with:
          args: >
            helm ${{ inputs.helm-action }} 
            --set image=cr.yandex/crp76aifpa9n0b74vbhm/${{ inputs.service-name }}:${{ steps.commit.outputs.short }}
            --set environment=Dev
            --set commit_hash=${{ steps.commit.outputs.short }}
            --set branch_name=${{ steps.extract_branch.outputs.branch }}
            --set top_secret=${{ secrets.TOP_SECRET }}
            ${{ inputs.service-name }} 
            -f Lab4/CloudsIntegration/.helm-charts/${{ inputs.service-name }}/${{ inputs.environment }}-values.yaml
            Lab4/CloudsIntegration/.helm-charts/${{ inputs.service-name }} 
            --namespace dumb
```
Тут тоже все не очень сложно, workflow получает на вход heml action, название сервиса и среду в котором надо задеплоить сервис, после чего достает нужную информацию (название ветки), а запускает helm для деплоя и передает ему параметры для шаблонизации yaml файлов - путь к образу, среду, секрет, и метаданные для того что бы в кубере можно было легко посмотреть откуда был задеплоен сервис.

### Финал
Собственно на этом все, CI/CD был протестирован, во всех режимах - просто сборка/просто деплой/сборка+деплой. Ниже приведен изображения, которые демонстрируют как выглядит в GitHub получившийся интерфейс.

Так же стоит отметить, вся работы проводилась на реальном облаке, и доступ к сайту есть сейчас по адрессу: http://130.193.35.166:30100/ (в поле ввода проверяется секрет который прокидывался через Github Actions, это строка: clouds)
_На момент вашего чтения сервис может не доступен, так как у  квота в облаке не бесконечная, я отключу его через две недели (надеюсь я не забыл потушить всю инфру :)_

![image](https://github.com/user-attachments/assets/b3c00013-114d-4eaa-8e6c-5a454570e8c7)
![image](https://github.com/user-attachments/assets/7400aad0-8c89-4a82-a83d-96e425318c8a)
![image](https://github.com/user-attachments/assets/f6816314-a78d-45d5-ad80-aac35c10afcf)
![image](https://github.com/user-attachments/assets/f075719f-cb7b-4b61-a21b-38c6640a94eb)




 
