import asyncio
from asyncio import subprocess


async def run_command(command: str):
    process = await asyncio.create_subprocess_shell(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = await process.communicate()
    assert process.returncode == 0, stderr.decode()

    return stdout.decode().strip()
