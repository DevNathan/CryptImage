"""
        Generate the watermark and embed it in the image which path is super.imageURL
"""
from hashlib import sha256
from os import lseek
from cryptimage.cryptImage import CryptImage
from cryptimage.cryptography import Cryptography
from cryptimage.neuralHash import NeuralHash
from scipy import misc
import qrcode
import numpy as np
import cv2
from PIL import Image,ImageDraw
from random import randint

class Watermark(CryptImage) : 
    watermark_str = "" # The string to embed in the image
    finalImageURL = "" # Final path of the image signed
    watermarkPosition = "" # un dictionnaire de la forme : {'top_left' : (x,y), 'top_right' : (x,y)}

    qrcodePath = "qrcode_genere.png" # PRIVATE. Path to the tmp qr code
    qrCodePixelsBytes = [] # Matrice stockant les pixels du QR code 1: blanc, 0: noir

    def __init__(self, imageURL, password):
        super().__init__(imageURL, password)
        
    
    """
        Manage the watermark creation 
        Return True or  raise an exception if fail
    """
    def mainWatermarkSignature(self):
        self.imageCopy() 
        print("[*] Creation de la nouvelle image nommée " + self.finalImageURL)

        print("[*] Génération de la signature  ...", end=' ')
        self.generateWatermarkString()
        print("Ok")

        print("[*] Génération du motif ...", end=' ')
        self.generateWatermarkImage()
        print("Ok")

        print("[*] Génération aléatoire d'une position dans l'image ...", end=' ')
        self.watermarkPosition = self.generateRandomPosition() 
        print("Ok")

        print("[*] Préparation du motif  ...", end=' ')
        self.stripQRCodeCorners()
        print("Ok")

        print("[*] Préparation des données du motif ...", end=' ')
        self.generateQrCodeMatrice()

        print("[*] Intégration du motif dans l'image ...", end=' ')
        self.emebedWatermark()
        print("Ok")

        return True

    """
        Extraction the watermark creation 
        Return True or  raise an exception if fail
    """
    def mainWatermarkVerify(self):
        self.imageCopy() 
        print("[*] Creation de la nouvelle image nommée " + self.finalImageURL)

        print("[*] Extraction des données constituant le motif ... ", end=' ')
        self.extractWatermark()
        print("Ok")

        print("[*] Reconstruction du motif 1/3 ... ", end=' ')
        self.reconstructQRCode()
        print("Ok")

        print("[*] Reconstruction du motif 2/3 ... ", end=' ')
        self.refaire_3_blocs()
        print("Ok")

        print("[*] Reconstruction du motif 3/3 ... ", end=' ')
        self.addBorder()
        print("Ok")

        print("[*] Extraction des données cotenus dans le motif ...", end=' ')
        self.readQRcode()
        print("Ok")

        print("[*] Verification de la preuve de propriété ...", end=' ')
        isOk =  self.checkWatermark()
        if not isOk:
            print("Ok")

        return isOk

        


   


    """
        Generate the string to embed in the watermark
    """
    def generateWatermarkString(self):
        neuralHash = NeuralHash()
        crypto = Cryptography(self.imageURL, self.password)

        imageHash = '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08'#neuralHash.neuralHash() for test purpose
        hash_password_binary = ''.join(format(ord(x), 'b').zfill(8) for x in crypto.hashed_password) # Encoding over 8 bits per char
        neuralHash_binary = ''.join(format(ord(x), 'b').zfill(8) for x in imageHash) # Encoding over 8 bits per char
        text_to_hash_binary = bin(int(hash_password_binary,2) | int(neuralHash_binary,2))[2:]
        text_to_hash_hexa = hex(int(text_to_hash_binary, 2))
        hashed_text = sha256(text_to_hash_hexa[2:].encode()).hexdigest()
        hashed_text_signed = crypto.sign(hashed_text)
        self.watermark_str = hashed_text + "," + hashed_text_signed




    """
        Generate the image related to the watermark
    """
    def generateWatermarkImage(self):
        qr = qrcode.QRCode(version=1,error_correction=qrcode.constants.ERROR_CORRECT_H,box_size=2,border=0)
        qr.add_data(self.watermark_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black",back_color="white").convert('RGB')
        img.save(self.qrcodePath)
        img.save("original.png")
        self.stripQRCodeCorners()

    """
    Enlever les 3 carrés délimitant le QRcode
    """    
    def stripQRCodeCorners(self):  
        print("strip corner") 
        qr = Image.open(self.qrcodePath)
        qr_code = np.array(qr) 
        transparent_area = (0,0,13,13) #carré en haut à gauche
        transparent_area2=(qr_code.shape[0]-14,0,qr_code.shape[0],13) #carré en haut à droite
        transparent_area3=(0,qr_code.shape[0]-14,13,qr_code.shape[0]) #carré en bas à gauche
        mask=Image.new('L', qr.size, color=255)
        draw=ImageDraw.Draw(mask) 
        draw.rectangle(transparent_area, fill=0)
        draw2=ImageDraw.Draw(mask)
        draw2.rectangle(transparent_area2, fill=0)
        draw3=ImageDraw.Draw(mask)
        draw3.rectangle(transparent_area3,fill=0)
        qr.putalpha(mask)
        qr.save(self.qrcodePath)

    """
    Replacer 1 bloc du QR code
    """
    def refaire_bloc(self,x,y):
        n=(0,0,0,255) #code d'un pixel noir
        b=(255,255,255,255)
        i2=j2=0
        im = Image.open(self.qrcodePath)
        pixels = im.load()
        matrice_pixels=[[n,n,n,n,n,n,n,n,n,n,n,n,n,n],[n,n,n,n,n,n,n,n,n,n,n,n,n,n],[n,n,b,b,b,b,b,b,b,b,b,b,n,n],[n,n,b,b,b,b,b,b,b,b,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,n,n,n,n,n,n,b,b,n,n],[n,n,b,b,b,b,b,b,b,b,b,b,n,n],[n,n,b,b,b,b,b,b,b,b,b,b,n,n],[n,n,n,n,n,n,n,n,n,n,n,n,n,n],[n,n,n,n,n,n,n,n,n,n,n,n,n,n]]
        for i in range(x,x+14):
            for j in range(y,y+14):
                pixels[i,j]=matrice_pixels[i2][j2]
                j2+=1
            i2+=1
            j2=0
        im.save(self.qrcodePath)

    """
    Replacer les 3 blocs du QR code
    """
    def refaire_3_blocs(self):
        self.refaire_bloc(0,0)
        self.refaire_bloc(len(self.qrCodePixelsBytes)-14,0)
        self.refaire_bloc(0,len(self.qrCodePixelsBytes)-14)

    """
        Copy and create the signed-image to be in the right location
    """
    def imageCopy(self):
        self.finalImageURL = "final.png"
        im = Image.open(self.imageURL)
        im.save(self.finalImageURL)
        


    """
        Verify if the image is encoded in PNG. If not, make the convertion
        If any conversion is made, the copied image is deleted and replaced by the converted one
    """

    def convertToPNG(self):
        img = Image.open(self.imageURL)
        try :
           if img.format!="PNG":
               splited = self.imageURL.split('.')
               if len(splited) == 1 or len(splited) == 2:
                   self.imageURL = splited[0] + ".png"
               else :
                   raise Exception("FATAL ERROR : The path to the file isn't correct") 

               img.save(self.imageURL)
        except :
           raise Exception("FATAL ERROR : The file isn't an image") 

    """
        Generate a random position in the image where the watermark CAN be embedded
    """
    def generateRandomPosition(self):
        im = Image.open(self.imageURL)
        width, height = im.size
        x_qr = randint(1,width - len(self.qrCodePixelsBytes)-1) #abscisse du QR code
        y_qr = randint(3,height - len(self.qrCodePixelsBytes)-1)  #ordonnée du QR code
        self.watermarkPosition = {"top_left":(x_qr, y_qr), "top_right":(x_qr + len(self.qrCodePixelsBytes), y_qr + len(self.qrCodePixelsBytes))}


    """ 
    Generate the tab associated to a QR code
    """

    def generateQrCodeMatrice(self):
        im = Image.open(self.qrcodePath)
        pixels = im.load()
        width, height = im.size    
        matrix = []

        for x in range(width):
            tmp = []
            for y in range(height):
 
                (r,g,b, a) = pixels[x,y]
                if a == 0:
                    tmp.append(-1)
                    
                elif (r,g,b) == (255,255,255):
                    tmp.append(1)
                else :
                    tmp.append(0)
            matrix.append(tmp)
        self.qrCodePixelsBytes = matrix
        
        
        
        
    """
        Embed the generated watermark (as an image) in the image
    """
    def emebedWatermark(self):
        (top_left_x, top_left_y) = self.watermarkPosition["top_left"]
        (top_right_x, top_right_y) = self.watermarkPosition["top_right"]

       
        im = Image.open(self.finalImageURL)
        pixelMap = im.load()
        x=0
        y=0
        for i in range(top_left_x, top_right_x+1):
            for j in range(top_left_y, top_right_y+3, 3):
                pixel = pixelMap[i,j]
                if im.mode == "RGB":
                    (r,g,b) = pixel
                else :
                    (r,g,b, a) = pixel
                (new_r, new_g, new_b) = (r,g,b)
                if j < top_right_y + 1:
                    if self.qrCodePixelsBytes[x][y] != -1:
                        new_r = int(str(bin(r)[2:-1]) + str(self.qrCodePixelsBytes[x][y]), 2)
                    else :
                        new_r = r
                if j+1 < top_right_y + 1:
                    if self.qrCodePixelsBytes[x][y+1] != -1:
                        new_g = int(bin(g)[2:-1] + str(self.qrCodePixelsBytes[x][y+1]), 2)
                    else :
                        new_g = g
                if j+2 < top_right_y + 1:
                    if self.qrCodePixelsBytes[x][y+2] != -1:
                        new_b = int(bin(b)[2:-1] + str(self.qrCodePixelsBytes[x][y+2]),2)
                    else :
                        new_b = b
                if im.mode == "RGB":
                    pixelMap[i,j] = (new_r, new_g, new_b)
                else :
                    pixelMap[i,j] = (new_r, new_g, new_b,a)
                y+=1
            x+=1
            y=0
        im.save(self.finalImageURL)





    """
        Extract the generated watermark (as an image) from the image
    """
    def extractWatermark(self):
        (top_left_x, top_left_y) = self.watermarkPosition["top_left"]
        (top_right_x, top_right_y) = self.watermarkPosition["bottom_left"]


        im = Image.open(self.imageURL)
        pixelMap = im.load()
        x=0
        y=0
        qrCodeExtracted = []
        for i in range(top_left_x, top_right_x+1):
            tmp = [] 
            for j in range(top_left_y, top_right_y+3, 3):
                pixel = pixelMap[i,j]
                if im.mode == "RGB":
                    (r,g,b) = pixel
                else:
                    (r,g,b, a) = pixel
                if j < top_right_y + 1:
                    tmp.append(str(bin(r)[-1]))
                if j+1 < top_right_y + 1:
                    tmp.append(str(bin(g)[-1]))
                if j+2 < top_right_y + 1:
                    tmp.append(str(bin(b)[-1]))
                y+=1
            qrCodeExtracted.append(tmp)
            x+=1
            y=0
        self.qrCodePixelsBytes = qrCodeExtracted
      
    
        """
            Test if the motif is correct according to the user 
            Return True is ok, False if not
        """
    def checkWatermark(self):
        neuralHash = NeuralHash()
        crypto = Cryptography(self.imageURL, self.password)

        imageHash =     '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08   '#neuralHash.neuralHash() for test purpose
        hash_password_binary = ''.join(format(ord(x), 'b').zfill(8) for     x in crypto.hashed_password) # Encoding over 8 bits per char
        neuralHash_binary = ''.join(format(ord(x), 'b').zfill(8) for x  in imageHash) # Encoding over 8 bits per char
        text_to_hash_binary = bin(int(hash_password_binary,2) | int (neuralHash_binary,2))[2:]
        text_to_hash_hexa = hex(int(text_to_hash_binary, 2))
        hashed_text = sha256(text_to_hash_hexa[2:].encode()).hexdigest()
            
        splited = self.watermark_str.split(',')
        if len(splited) != 2:
            print("\n\n[!] REQUEST REJECTED [!]\n You are NOT the rightfull owner\n\n")
            return False

        extractedHash = splited[0]
        extractedSignature = splited[1]

            # First step : Verify the signature 
        if not crypto.verify_signature(extractedSignature, extractedHash):
            print("[!] REQUEST REJECTED [!]\n You are NOT the rightfull owner ")
            return False 
        print(extractedHash)
        print(hashed_text)
        if extractedHash == hashed_text :
            return True 
        else : 
            print("[!] REQUEST REJECTED [!]\nYou are NOT the rightfull owner ")
            return False
            

            
    """
    Reconstruit le qr code à partir de la matrice
    """
    def reconstructQRCode(self):
        print("test")
        self.qrcodePath = "tmpQR.png"
        qrcode = Image.new(mode="RGB", size=(len(self.qrCodePixelsBytes),len(self.qrCodePixelsBytes)), color="white")
        qrcode.save(self.qrcodePath)
        pixels = qrcode.load()

        width, height = qrcode.size
        pixels = qrcode.load()
        i=0
        j=0
        for x in range(width):
            for y in range(height):
                if self.qrCodePixelsBytes[i][j] == -1:
                    pixels[x,y] = 0,0,0
                elif self.qrCodePixelsBytes[i][j] == 1:
                     pixels[x,y] = 255,255,255
                else :
                     pixels[x,y] = 0,0,0
                j+=1
            i+=1
            j=0
        qrcode.save(self.qrcodePath)
        self.stripQRCodeCorners()

    
    """
        Add border to a qr code
    """
    def addBorder(self):
        qrcode = Image.new(mode="RGB", size=(len(self.qrCodePixelsBytes)+8,len(self.qrCodePixelsBytes )+ 8), color="white")
        old = Image.open(self.qrcodePath)
        width,_ = qrcode.size
        old_pixels = old.load()
        newPixels = qrcode.load()
        i,j = 0,0
        for x in range(4,width-4):
            for y in  range(4,width-4):
                newPixels[x,y] = old_pixels[i,j]
                j+=1
            i+=1 
            j=0
        qrcode.save(self.qrcodePath)

        


    """
    Read the qr code data 
    """
    def readQRcode(self):
        print(self.qrcodePath)
        image = cv2.imread(self.qrcodePath)
        # initialize the cv2 QRCode detector
        detector = cv2.QRCodeDetector()
        # detect and decode
        data, vertices_array, _ = detector.detectAndDecode(image)
        # if there is a QR code
        # print the data
        if vertices_array is not None:
            self.watermark_str = data
        else :
            raise Exception("FATAL ERROR : The watermark is corrupted")



        


        


