"""
        Generate the string related to the watermark position to embed in the LSB of image
"""
from cryptimage.aes import AESCipher
from cryptimage.cryptography import Cryptography
from cryptimage.watermark import Watermark
from PIL import Image
import base64
import json
class LSB(Watermark):
    lsb_str = "" # The string to embed in LSB

    def __init__(self, imageURL, password):
        super().__init__(imageURL, password)
    """
        Manage the LSB creation and embedding
        Return True or  raise an exception if fail
    """
    def main(self):
        self.generateLSBstring()
        self.embedInLSB()

    """
        Genere le message chiffre a integrer dans les LSB
    """
    def generateLSBstring(self):
        position = self.watermarkPosition
        print(position)
        position_str = json.dumps(position)
        crypto = Cryptography(self.imageURL, self.password)
        aes = AESCipher(crypto.unique_key)
        self.lsb_str = aes.encrypt(position_str).decode()
        


    """
       Code le message dans la premiere colonne de pixel de l'image
    """
    def embedInLSB(self):
        #Importation de l'image a encoder
        im = Image.open("original.png")
        width, height = im.size
        pixels = im.load()

        if self.lsb_str == "":
            raise Exception("FATAL ERROR : There is no string to embed in LSB") 
        #print(self.lsb_str)
        bin_lsb_str = ''.join(format(ord(x), 'b').zfill(8) for x in self.lsb_str)        #Conversion en binaire du Str à encoder
        i = 0
        for x in range(0, len(bin_lsb_str), 3):              #On parcourt la premiere ligne de pixel de longueur notre message
            #print(pixels[x,0])
            r,g,b,_=pixels[x,0]                        

            if i<len(bin_lsb_str):
                r_bit, g_bit, b_bit = bin(r), bin(g), bin(b)
                r_lsb, g_lsb, b_lsb = int(r_bit[-1]), int(g_bit[-1]), int(b_bit[-1])           #On extrait les LSB de chaque code rgb
                new_r_lsb, new_g_lsb, new_b_lsb = bin_lsb_str[i], bin_lsb_str[i+1], bin_lsb_str[i+2]       #On modifie chaque R G B avec le code voulu
                
                #On reconstitue nos octets pour chaque R G B
                final_embed_r_bit = int(r_bit[:-1] + str(new_r_lsb), 2)
                final_embed_g_bit = int(g_bit[:-1] + str(new_g_lsb), 2)
                final_embed_b_bit = int(b_bit[:-1] + str(new_b_lsb), 2)


        #On code nos otets dans l'image
        #print (pixels[x,0])
        pixels[x,0] = (final_embed_r_bit, final_embed_g_bit, final_embed_b_bit)
        print(pixels[x,0])
        
        im.save("original.png")


#Penser a passer a la ligne si on depasse la longueur de l'image par rapport a la longueur du 



