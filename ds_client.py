import socket
import ds_protocol as protocol
import json




def send(server:str, port:int, username:str, password:str, post, bio, profile):
    try:
        PORT = port
        HOST = server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
            client.connect((HOST, PORT))                                #connecting to the given IP address and port

            send = client.makefile('w')
            recv = client.makefile('r')
            print(f'Sending profile to server {HOST}')
            print()

            join_msg = protocol.join_generate(username = username, password = password, my_public_key = profile.public_key)
            send.write(join_msg + '\n')
            send.flush()

            print('Loading...')
            
            srv_msg = recv.readline()                      #server responding
                
            response = protocol.response_generate(srv_msg) # type, message, token
                
            if response.type == 'ok':
                server_public_key = response.token

                #encrypt the post message and bio to send to the server
                en_msg = profile.encrypt_entry(post.get_entry(), server_public_key).decode(encoding = 'UTF-8')
                en_bio = profile.encrypt_entry(bio, server_public_key).decode(encoding = 'UTF-8')
                

                print(response.message)
                print()

                
                if en_msg != None and en_msg != '': #posting on the server
                    post_msg = protocol.post_generate(profile.public_key, en_msg, 0)
                    send.write(post_msg + '\n')
                    send.flush()

                    post_res = recv.readline()
                    post_response = protocol.response_generate(post_res)
                    if post_response.type == 'ok':
                        print('Sucessfully Posted!')
                        print()
                        print(post_response.message)
                    elif post_response.type == 'error':
                        print("ERROR: " + post_response.message)

                if bio != None and bio != '':   #edit bio on the server
                    bio_msg  = protocol.bio_generate(profile.public_key, en_bio, 0)
                    send.write(bio_msg + '\n')
                    send.flush()

                    bio_res = recv.readline()
                    bio_response = protocol.response_generate(bio_res)
                    if bio_response.type == 'ok':
                        print('Bio Updated!')
                        print()
                        print(bio_response.message)
                    elif bio_response.type == 'error':
                        print('ERROR: ' + bio_response.message)
                        

            elif response.type == 'error':
                print('ERROR:  ' + response.message)
                return

    except Exception as ex:
        print(ex)
    

