from flask import Flask, render_template, redirect ,url_for, request, session, jsonify
import mysql.connector
from config import get_db, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY


@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        kullanici_ad = request.form['ad']
        kullanici_mail = request.form['mail']

        try:
            db = get_db()
            cursor = db.cursor(dictionary=True)


            cursor.execute("SELECT * FROM kullanici WHERE ad = %s AND mail = %s", (kullanici_ad, kullanici_mail))
            kullanici = cursor.fetchone()

            cursor.close()
            db.close()

            if kullanici:
                session['kullanici_id'] = kullanici['id']
                session['kullanici_ad'] = kullanici['ad']
                return redirect(url_for('home'))
            else:
                db = get_db()
                cursor = db.cursor(dictionary=True)
                cursor.execute("INSERT INTO kullanici (ad, mail) Values (%s, %s)", (kullanici_ad, kullanici_mail))
                db.commit()
                session['kullanici_id'] = cursor.lastrowid
                session['kullanici_ad'] = kullanici_ad

                cursor.close()
                db.close()
                return redirect(url_for('home'))
        except mysql.connector.IntegrityError:
            return "Kayıtlı mail adresi"
    
    return render_template('index.html')


@app.route('/home')
def home():
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM deste WHERE kullanici_id = %s", (session['kullanici_id'],))
    kulanici_deste = cursor.fetchall()

    cursor.execute("SELECT * FROM deste WHERE kullanici_id = 1")
    admin_deste = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('home.html', kullanici_deste=kulanici_deste,
                                admin_deste=admin_deste,
                                kullanici_ad=session['kullanici_ad'],)
@app.route('/desteler')
def desteler():
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM deste WHERE kullanici_id = %s", (session['kullanici_id'],))
    kulanici_deste = cursor.fetchall()

    cursor.execute("SELECT * FROM deste WHERE kullanici_id = 1")
    admin_deste = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('desteler.html', kullanici_deste=kulanici_deste,
                                admin_deste=admin_deste,
                                kullanici_ad=session['kullanici_ad'],)

@app.route('/study/<int:deste_id>')
def study(deste_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM deste WHERE id = %s", (deste_id,))
    deste = cursor.fetchone()

    cursor.execute("SELECT * FROM kart WHERE deste_id = %s ORDER BY id", (deste_id,))
    kart = cursor.fetchall()

    cursor.close()
    db.close()


    return render_template('study.html', deste=deste, kart=kart,)


@app.route('/kart_liste/<int:deste_id>')
def kart_liste(deste_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM deste WHERE id = %s", (deste_id,))
    deste = cursor.fetchone()

    cursor.execute("SELECT * FROM kart WHERE deste_id = %s ORDER BY id", (deste_id,))
    kartlar = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template('kart_liste.html', deste=deste, kartlar=kartlar)


@app.route('/fav_ekle/<int:kart_id>')
def fav_ekle(kart_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT fav, deste_id FROM kart WHERE id = %s", (kart_id,))
    kart = cursor.fetchone()
        
    if kart:
        cursor.execute("UPDATE kart SET fav = NOT fav WHERE id = %s", (kart_id,))
        db.commit()
            
        return redirect(url_for('study', deste_id=kart['deste_id'],))
    
    

@app.route('/favoriler')
def favoriler():
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        cursor.execute("""
            SELECT kart.*, deste.baslik 
            FROM kart 
            LEFT JOIN deste ON kart.deste_id = deste.id 
            WHERE kart.kullanici_id = %s AND kart.fav = 1 
            ORDER BY kart.id   
        """, (session['kullanici_id'],))
        
        kartlar = cursor.fetchall()
        
        
        cursor.close()
        db.close()

        return render_template('favoriler.html', 
                              kartlar=kartlar, 
                              kullanici_ad=session['kullanici_ad'],)
    
    except Exception as e:
        print(f"Favoriler hatası: {e}")
        return "Bir hata oluştu"


@app.route('/deste_ekle', methods=['GET', 'POST'])
def deste_ekle():
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        baslik = request.form['baslik']
        aciklama = request.form['aciklama']

        db = get_db()
        cursor = db.cursor()

        cursor.execute("INSERT INTO deste (baslik, aciklama, kullanici_id) VALUES (%s, %s, %s)", (baslik, aciklama, session['kullanici_id']))
        db.commit()
        deste_id = cursor.lastrowid

        cursor.close()
        db.close()

        return redirect(url_for('kart_ekle', deste_id=deste_id))
    
    return render_template('deste_ekle.html')

@app.route('/kart_ekle/<int:deste_id>', methods=['GET', 'POST'])
def kart_ekle(deste_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        on_yazi = request.form['on_yazi']
        arka_yazi = request.form['arka_yazi']
        cumle = request.form.get('cumle', '')

        db = get_db()
        cursor = db.cursor()

        cursor.execute("INSERT INTO kart (on_yazi, arka_yazi, cumle, kullanici_id, deste_id) VALUES (%s, %s, %s, %s, %s)"
                       , (on_yazi, arka_yazi, cumle, session['kullanici_id'], deste_id))
        
        db.commit()

        cursor.close()
        db.close()

        return redirect(url_for('kart_ekle', deste_id=deste_id))
    
    return render_template('kart_ekle.html', deste_id=deste_id)


@app.route('/kart_update/<int:kart_id>', methods=['GET', 'POST'])
def kart_update(kart_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    if request.method == 'POST':
        on_yazi = request.form['on_yazi']
        arka_yazi = request.form['arka_yazi']
        cumle = request.form.get('cumle', '')

        cursor.execute(""" UPDATE kart
                       SET on_yazi = %s, arka_yazi =%s, cumle =%s
                       WHERE id = %s AND kullanici_id = %s """, 
                       (on_yazi, arka_yazi, cumle, kart_id, session['kullanici_id'],
                        ))
        
        db.commit()
        

        cursor.execute("SELECT deste_id FROM kart WHERE id = %s", (kart_id,))
        kart = cursor.fetchone()
        deste_id = kart['deste_id']

        cursor.close()
        db.close()

        return redirect(url_for('kart_liste', deste_id=deste_id))

        
    cursor.execute("SELECT * FROM kart WHERE id = %s AND kullanici_id = %s", (kart_id, session['kullanici_id']))
    kart = cursor.fetchone()
    cursor.close()
    db.close()

    return render_template('kart_update.html', kart=kart)
    

@app.route('/kart_delete/<int:kart_id>')
def kart_delete(kart_id):
    if 'kullanici_id' not in session:
        return redirect(url_for('login'))
    
    db = get_db()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT deste_id FROM kart WHERE id = %s", (kart_id,))
    kart = cursor.fetchone()
    deste_id = kart['deste_id']

    cursor.execute("DELETE FROM kart WHERE id = %s", (kart_id,))

    db.commit()
    cursor.close()
    db.close()

    return redirect(url_for('kart_liste', deste_id=deste_id))

@app.route('/deste_sil/<int:deste_id>')
def deste_delete(deste_id):
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute("DELETE FROM kart WHERE deste_id = %s", (deste_id,))
    
    cursor.execute("DELETE FROM deste WHERE id = %s", (deste_id,))
    
    db.commit()
    cursor.close()
    db.close()
    
    return redirect(url_for('home'))



@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
        




















