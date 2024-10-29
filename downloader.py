import asyncio
import logging
import os
import sys
from time import time

import yadisk
from dotenv import load_dotenv
from yadisk.objects import ResourceObject, DiskInfoObject
import psutil
from pathlib import Path


from lib.api360 import API360

load_dotenv()

process = psutil.Process()


directories: list[ResourceObject] = []

log = logging.getLogger('Downloader')
log.setLevel(logging.INFO)
log_handler = logging.StreamHandler(sys.stdout)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(message)s'))
log.addHandler(log_handler)

async def main(email: str):
    start_time = time()
    api = API360(api_key=os.getenv('TOKEN'), org_id=os.getenv('ORG_ID'), log_level=logging.DEBUG)
    response = {}
    try:
        response = await api.get_service_app_token(
            client_id=os.getenv('CLIENT_ID'),
            client_secret=os.getenv('CLIENT_SECRET'),
            subject_token=email,
            subject_token_type='urn:yandex:params:oauth:token-type:email'
        )
    except Exception as e:
        log.debug(f'Failed to get service app token: {e}')
        exit(1)
    token = response['access_token']
    # print(token)
    client = yadisk.AsyncClient(token=token)

    async with client:

        if await client.check_token():
            log.info(f'Test service app token: Success')
        else:
            log.error(f'Test service app token: Failed')
            exit(1)

        disk_info: DiskInfoObject = await client.get_disk_info()

        log.info(f'Starting files download for user: {email}')
        log.info(f'Used disk space: {round(disk_info.used_space / 1024 ** 2, 2)} MB')

        log.info('Listing user directories...')

        await list_directory(client, '/')

        log.debug(f'Used memory {round(process.memory_info().rss / 1024 ** 2, 2)} MB')

        log.info(f'Found directories count: {len(directories)}')
        log.info('Listing user files...')
        files = await list_files(client)
        log.debug(f'Used memory {round(process.memory_info().rss / 1024 ** 2, 2)} MB')
        files_count = len(files)
        log.info(f'Found files to download: {files_count}')
        log.info('Downloading user files...')

        sem = asyncio.Semaphore(5)

        for directory in directories:
            path = email + directory.path.removeprefix('disk:')
            log.debug(f'Creating directory: {path}')
            Path(path).mkdir(parents=True, exist_ok=True)

        file_position = 1
        for file in files:

            # log.debug(directory.path)
            file_position_str = f'[{file_position}/{files_count}]'
            file_position += 1
            await download_file(
                client=client,
                path=file.path.removeprefix('disk:'),
                email=email,
                file_position_of=file_position_str,
                sem=sem
            )

        end_time = time()
        log.info(f'Downloaded {len(files)} files in {round((end_time - start_time) / 60, 2)} minutes')
        log.debug(f'Used memory {round(process.memory_info().rss / 1024 ** 2, 2)} MB')

async def download_file(client, path, email, file_position_of, sem):
    try:
        async with sem:  # Don't start next download until 10 other currently running
            log.debug(f'Downloading file {file_position_of}: {path}')
            await client.download(path, f'{email}{path}')

    finally:
        # log.debug(f"Complete download: {path}")
        pass


async def process_directories(client, directories_list):
    if len(directories_list) > 0:
        # log.debug(f'Starting to process {len(directories_list)} directories')

        for directory in directories_list:
            # log.debug(f'Process directory: {directory.path}')
            # log.debug('PD: Waiting to keep rps')
            await asyncio.sleep(0.1)
            # log.debug('PD: Done waiting sleep')
            await list_directory(client, directory.path)
            # log.debug('PD: Done process dir')


async def list_directory(client, path):
    global directories
    directories_list: list[ResourceObject] = []

    async for item in client.listdir(path):
        if item.type == 'dir':
            # log.debug(f'Add directory: {item.path}')
            directories_list.append(item)
    directories.extend(directories_list)
    await process_directories(client, directories_list)

async def list_files(client) -> list[ResourceObject]:
    files_list: list[ResourceObject] = []
    async for item in client.listdir('/'):
        if item.type == 'file':
            files_list.append(item)
            # log.debug(f'Add file: {item.path}')
    for directory in directories:
        async for item in client.listdir(directory.path):
            if item.type == 'file':
                files_list.append(item)
                # log.debug(f'Add file: {item.path}')
        await asyncio.sleep(0.1)
    return files_list



if __name__ == "__main__":
    user_email = input('Enter user email: ')
    asyncio.run(main(email=user_email))