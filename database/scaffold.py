import os

import asyncio
import asyncpg
import re
import logging

logging.basicConfig(level=logging.INFO)

pattern = re.compile(r"(?<!^)(?=[A-Z])")


def write_model_to_file(file_name: str, body: str):
    f = open(file_name, "w")
    f.write(body)
    f.close()


async def get_pool(connection_string: str):
    return await asyncpg.create_pool(dsn=connection_string)


async def generate(
    connection_string: str,
    schema_name: str = "public",
    separate_file: bool = True,
    model_directory: str = "models",
    overwrite: bool = True,
    create_folder_if_not_exist: bool = True,
):
    pool = await get_pool(connection_string,)
    if not os.path.isdir(model_directory):
        if create_folder_if_not_exist:
            os.mkdir(model_directory)
            logging.info(f"Creating directory {model_directory}")
        else:
            raise FileNotFoundError(f"{model_directory} directory doesn't exist")

    sql = f"""select * from "{schema_name}".generate_dataclass($1, $2)"""

    logging.info(
        f'Data models will be writed into {"separated files" if separate_file else "one file called FullDump.py"}'
    )

    async with pool.acquire() as con:
        logging.debug(f"Fetching results from db...")
        result = await con.fetch(sql, schema_name, separate_file)
        logging.debug(f"Fetched results from db")
        for table_data in result:
            t_name = table_data["table_name_generated"]
            t_declaration = table_data["declaration_generated"]
            logging.info(f"Processing {t_name}")

            file_name = model_directory + "/" + pattern.sub("_", t_name).lower() + ".py"

            if os.path.isfile(file_name):
                if not overwrite:
                    logging.warning(
                        f"{overwrite=} and file {file_name} is exist can't write file"
                    )
                    continue

            write_model_to_file(file_name, t_declaration)
            logging.info(f"Writed {t_name} to file {file_name}")


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(generate("", separate_file=True))
