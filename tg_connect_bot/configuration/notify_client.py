import decouple
import json
import asyncio


async def tcp_echo_client(email, letter, resp):

    msg = {'email': email,
           'letter': letter,
           'resp': resp
           }
    # Connect to the server
    host = decouple.config('NOTIFY_HOST')
    port = int(decouple.config('NOTIFY_PORT'))
    reader, writer = await asyncio.open_connection(host, port)
    json_data = json.dumps(msg)
    # Send a message to the server
    writer.write(json_data.encode())
    await writer.drain()
    print(f'[tcp_echo_client] SENT TO CLIENT: {json_data!r}')
    # Receive the response from the server
    data = await reader.read(100)
    print(f'[tcp_echo_client] FROM SERVER RECEIVED: {data.decode()!r}')
    # Close the connection
    writer.close()
    await writer.wait_closed()

# asyncio.run(tcp_echo_client({'email':'connecttoyelp+43423@gmail.com', 'letter':'User_letter', 'resp':"User_resppp"}))
