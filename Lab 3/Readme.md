# Лабораторная работа 3
## Kubernetes

Kubernetes — система оркестровки контейнеров с открытым исходным кодом, готовая для production и предназначенная для автоматизации размещения, масштабирования и управления контейнерами.

Для начала работы в с кластером кубернетеса и его изучения, его надо развернуть локально, самым простым способом для этого является использование minikube. Вся работа будет продемонстрирована на MacOS, альтернативные команды для остальных ОС можно найти на оффициальном сайте minikube: https://kubernetes.io/ru/docs/tasks/tools/install-minikube/

Пройдем шаги установки minikube и всех необходимых для работы утилит по порядку:
1. Необходимо установить kubectl - командную утилиту для управления кластерами кубернетеса, позволяющая просматривать и редактировать ресурсы и конфиги множества кластеров:
```brew install kubectl ```
2. Затем проверим, что kubectl успешно установился:
```kubectl version --client```
3. После установки kubectl, установим сам minikube, который развернет нам локальный кластер с единственной нодой:
```brew install minikube```
4. Так же проверим, что minikube успешно установился:
```minikube status```
5. Запустим minikube
```minikube start```
Готово, все необходимое установлено, и теперь можно переходить к конфигурацию и запуска нашего локального кластера.
> Скриншотов по процессу установки к сожалению не будет, так как kubectl и minikube были установлены у меня уже очень давно

Так же учтите, что minikube требует некое минимальное количество аппаратных ресурсов, так у меня докеру было выделено всего 3 CPU, а minikube надо 4, и при запуске minikube выдал мне следующую ошибку при запуске:
```
😄  minikube v1.32.0 на Darwin 14.6.1 (arm64)
✨  Используется драйвер docker на основе существующего профиля
- Ensure your docker daemon has access to enough CPU/memory resources.
- Docs https://docs.docker.com/docker-for-mac/#resources

⛔  Exiting due to RSRC_INSUFFICIENT_CORES: Requested cpu count 4 is greater than the available cpus of 3
```
В данной ситуации просто измените доступные ресурсы для докера, перезапустите его, и попробуйте запустить minikube заново.

## Minikube
Перейдем к запуску кластера, в котором будем поднимать поды, деплойменты, сервисы и остальные компоненты кластера. Но предварительно хотелось бы ввести некоторую пометку, если вы собираетесь использовать ваши личные, находящиеся локальные образы докера, просто так это сделать не получиться, для этого надо запускать minikube следующим способом:
1. Запустим minikube в окружении докера
```eval $(minikube -p minikube docker-env)```
2. Сбилдим наши образы находясь в контексте командной строки в которой ввели преыдущую комманду
3. Во всех конфиг файлах, которые управляют подами, выставим для них
```imagePullPolicy: Never```
4. Готово, можно применять конфигурационные файлы ресурсов, использующих ваши локальные образы докера

Переходя к запуску, введем команду
```minikube start```
И получим нечто подобное
```
😄  minikube v1.32.0 на Darwin 14.6.1 (arm64)
✨  Используется драйвер docker на основе существующего профиля
👍  Запускается control plane узел minikube в кластере minikube
🚜  Скачивается базовый образ ...
🔄  Перезагружается существующий docker container для "minikube" ...
🐳  Подготавливается Kubernetes v1.28.3 на Docker 24.0.7 ...
🔗  Configuring bridge CNI (Container Networking Interface) ...
🔎  Компоненты Kubernetes проверяются ...
💡  After the addon is enabled, please run "minikube tunnel" and your ingress resources would be available at "127.0.0.1"
    ▪ Используется образ registry.k8s.io/ingress-nginx/controller:v1.9.4
    ▪ Используется образ gcr.io/k8s-minikube/storage-provisioner:v5
    ▪ Используется образ registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20231011-8b53cabe0
    ▪ Используется образ registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20231011-8b53cabe0
🔎  Verifying ingress addon...
🌟  Включенные дополнения: storage-provisioner, ingress, default-storageclass
🏄  Готово! kubectl настроен для использования кластера "minikube" и "default" пространства имён по умолчанию
```
У вас может не быть следующих строк, или они могут быть другими, так и должно быть, это плагины которые я установил дополнительно к minikube, один из них - ingress
```
💡  After the addon is enabled, please run "minikube tunnel" and your ingress resources would be available at "127.0.0.1"
    ▪ Используется образ registry.k8s.io/ingress-nginx/controller:v1.9.4
    ▪ Используется образ gcr.io/k8s-minikube/storage-provisioner:v5
    ▪ Используется образ registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20231011-8b53cabe0
    ▪ Используется образ registry.k8s.io/ingress-nginx/kube-webhook-certgen:v20231011-8b53cabe0
🔎  Verifying ingress addon...
🌟  Включенные дополнения: storage-provisioner, ingress, default-storageclass
```
Супер, наш кластер поднят, теперь надо это проверить, и по необходимости (если у вы до этого уже работали с kubectl) переключится на его контекст, проверим и переключимся на него следующими командами:
```kubectl config get-contexts``` - Выведет доступные кластеры, к которым подключен ваш kubectl, среди них должен быть ```minikube```
```kubectl config use-context minikube``` - Переключит вас в контекст minikube кластера, и выведет ```Switched to context "minikube".``` в случае успеха.

### Work in progress