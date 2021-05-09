from flask import *  
from PIL import ImageOps,Image
from firebase_admin import credentials, initialize_app, storage,db
import os

cred = credentials.Certificate("key.json")
initialize_app(cred, {'storageBucket': 'image-compression-heroku.appspot.com'})
ref = db.reference("/",url = 'https://image-compression-heroku-default-rtdb.asia-southeast1.firebasedatabase.app/')
app = Flask(__name__, template_folder='templates')  


@app.route('/')  
def upload():  
    return render_template("index.html")  
 
@app.route('/success', methods = ['POST'])  
def success(): 
    path = "images/original/" 
    if request.method == 'POST':  
        f = request.files['file']
        ps = path+f.filename
        f.save(ps)
        fileName = f.filename
        bucket = storage.bucket()
        blob1 = bucket.blob(fileName)
        blob1.upload_from_filename(ps)
        blob1.make_public()
        l1 = blob1.public_url
        img = Image.open(ps)    
        
        # Compressing the image
        compname = "/compressed_"+f.filename
        blob2 = bucket.blob(compname)
        
        if(request.form['comp']==''):
            img.save('images/compressed'+compname,optimize=True,quality=30)
            blob2.upload_from_filename('images/compressed'+compname)
            blob2.make_public()
        else:
            img.save('images/compressed'+compname,optimize=True,quality=int(request.form['comp']))
            blob2.upload_from_filename('images/compressed'+compname)
            blob2.make_public()
        
        # Setting the links in firebase
        ref.set({"out_link":blob2.public_url,
                 "out_file_size":os.path.getsize('images/compressed'+compname),
                 "original_link":blob1.public_url,
                 "original_file_size":os.path.getsize(ps)}) 

        return redirect(blob2.public_url)  
         
if __name__ == '__main__':  
    app.run()