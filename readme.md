## Tools collection for Yandex 360 API

Add .env file with content:

```
TOKEN=yandex_360_api_token
ORG_ID=organizaton_id
CLIENT_ID=service_application_client_id
CLIENT_SECRET=service_application secret
```

- yandex_360_api_token:
  - https://yandex.ru/dev/api360/doc/ru/access
- organization_id:
  - From admin panel https://admin.yandex.ru/
- service_application_client_id: 
  - https://yandex.ru/support/yandex-360/business/admin/ru/security-service-applications



- `listusers.py` - export all organization to .csv file. Required token scope: `directory:read_users` 
 - `downloader.py` - download all user files from Yandex Disk. Required access rights:
`cloud_api:disk.app_folder, cloud_api:disk.read, cloud_api:disk.info,
  yadisk:disk`. More info: https://yandex.ru/dev/api360/doc/ru/ref/ServiceApplicationsService/ServiceApplicationsService_Create.html