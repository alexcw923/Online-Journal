# TODO: Install the pynacl library so that the following modules are available
# to your program.
import nacl.utils
from nacl.public import PrivateKey, PublicKey, Box
from OnlineJournal.Profile import Profile, Post, DsuFileError, DsuProfileError
import NaClDSEncoder
from NaClDSEncoder import NaClDSEncoder
import json, os
from pathlib import Path
    
# TODO: Subclass the Profile class
class NaClProfile(Profile):
    def __init__(self, dsuserver = None, username = None, password = None):
        super().__init__(dsuserver, username, password)

        self.keypair = self.generate_keypair()
        self.public_key = self.keypair[0:44]
        self.private_key = self.keypair[44:88]
        
    def generate_keypair(self) -> str:

        gen = NaClDSEncoder()
        gen.generate()


        self.public_key = gen.public_key
        self.private_key = gen.private_key
        self.keypair = gen.keypair
        return self.keypair
        

    def import_keypair(self, keypair: str):
        try:
            self.keypair = keypair
            self.public_key = keypair[0:44]
            self.private_key = keypair[44:88]
            print('Key imported')
        except IndexError:
            print('The the length of the given keypair is wrong, it should be 88 (44 for public key and 44 for private key.')


    def add_post(self, post: Post) -> None:
        encrypted_post = self._encrypt(entry = post['entry'], private_key = self.private_key, public_key = self.public_key)
        post = Post(entry = encrypted_post, title = post['title'])

        
        super().add_post(post)

    def get_posts(self) -> list:
        decrypted_posts = []
        try:
            for post in super().get_posts():
                entry = post.get_entry()
                timestamp = post.get_time()
                title = post.get_title()

                d_post = self._decrypt(encrypted = entry, private_key = self.private_key, public_key = self.public_key)


                decrypted_posts.append(Post(d_post, timestamp, title))
            return decrypted_posts
            
        
        except Exception as ex:
            raise(DsuProfileError(ex))
        
            
    
    def load_profile(self, path: str) -> None:
        p = Path(path)

        if os.path.exists(p) and p.suffix == '.dsu':
            try:
                f = open(p, 'r')
                obj = json.load(f)
                self.username = obj['username']
                self.password = obj['password']
                self.dsuserver = obj['dsuserver']
                self.bio = obj['bio']

                self.private_key = obj['private_key']
                self.public_key = obj['public_key']
                self.keypair = obj['keypair']

                for post_obj in obj['_posts']:
                    post = Post(post_obj['entry'], post_obj['timestamp'], post_obj['title'])
                    self._posts.append(post)
                f.close()
            except Exception as ex:
                raise DsuProfileError(ex)
        else:
            raise DsuFileError()
    

    def _box_gen(self, private_key, public_key) -> Box: #generate box object with the Box function
        ne = NaClDSEncoder()
        pvobj = ne.encode_private_key(private_key) #PrivateKey()
        pcobj = ne.encode_public_key(public_key)   #PublicKey()
        return Box(pvobj, pcobj)


    def _encrypt(self, entry: str, private_key, public_key) -> str: #encrypt any entry with the keys
        obj = self._box_gen(private_key, public_key)
        entry_en = entry.encode('UTF-8')
        encrypted = obj.encrypt(entry_en, encoder=nacl.encoding.Base64Encoder)

        return encrypted.decode(encoding = 'UTF-8')
        

    def _decrypt(self, encrypted: str, private_key, public_key) -> str: #decrypt entry
        try:
            obj = self._box_gen(private_key, public_key)
            en_bytes = encrypted.encode('UTF-8')
            decrypted = obj.decrypt(en_bytes, encoder=nacl.encoding.Base64Encoder)

            return decrypted.decode(encoding = 'UTF-8')
        except Exception as ex:
            raise(DsuProfileError(ex))


            

    def encrypt_entry(self, entry:str, public_key:str) -> bytes:
        try:
            encrypted = self._encrypt(entry, self.private_key, public_key)
            en_str = encrypted.encode(encoding = 'UTF-8')
        except Exception as ex:
            raise DsuProfileError(ex)

        return en_str