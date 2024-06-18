from flask import Flask, render_template, request, redirect, url_for,flash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'chello'
em = ""

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='/.,m',
        database='vedaa'
    )

def create_triggers():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TRIGGER if not exists stock_update
        AFTER INSERT ON buy
        FOR EACH ROW
        BEGIN
            -- Decrease the stock by one for the purchased medicine
            UPDATE medicines
            SET stock = stock - 1
            WHERE name = NEW.name;  -- Assuming 'name' is the attribute in the 'buy' table
        END
    ''')

    conn.commit()
    conn.close()


    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TRIGGER if not exists track_failed_login_attempts
        AFTER INSERT ON failed_login
        FOR EACH ROW
        BEGIN
            DECLARE attempts INT;
            SELECT COUNT(*) INTO attempts
            FROM failed_login
            WHERE customer_id = NEW.customer_id
                AND TIMESTAMPDIFF(MINUTE, created_at, NOW()) <= 10;  -- Count failed attempts within the last 10 minutes
            IF attempts >= 3 THEN
                UPDATE customer
                SET blocked = 1
                WHERE customer_id = NEW.customer_id;
            END IF;
        END
    ''')

    conn.commit()
    conn.close()
    print("kkkkk")


@app.route('/', methods=['GET'])
def signin_form():
    return render_template('dbms5/sign-in/index.html')

@app.route('/', methods=['POST'])
def signin():
    
    if(request.form["action"] == "su"):
        return redirect(url_for("signup"))
    password = str(request.form['ps'])
    
    email = request.form['em']
    global em
    em = email
    conn = get_db_connection()
    cursor = conn.cursor()
    ss = cursor.execute('select name from customer where Email = %s and passwd = %s',(email,password) )
    results = cursor.fetchall()  
    conn.commit() 
    if results:
        sss = cursor.execute('select blocked from customer where Email = %s and passwd = %s',(email,password) )
        resultss = cursor.fetchall()  
        print(resultss)
        if resultss[0][0] == None:

            if(request.form["action"] == "si"):
                return redirect(url_for("home"))
        else:
            flash("You have been blocked☠️")
            flash("To unblock contact admin")
            return redirect(url_for("signin"))
    else:
        ss = cursor.execute('select customer_id from customer where Email = %s',(email,) )
        result = cursor.fetchall() 
        print(result)
        if result:

            sss = cursor.execute('Insert into failed_login (customer_id) values (%s)',(result[0][0],))
            conn.commit()
            conn.close()
            print(result[0][0])
            resultss = cursor.fetchall()  
    return redirect(url_for("signin"))
@app.route('/home', methods=['GET'])
def home_form():
    return render_template('dbms5/album/index.html')
    

@app.route('/home', methods=['POST'])
def home():
    medicine_name = request.form['medicine_name']
    print(medicine_name)
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.form["m1"] == "m1":

        cursor.execute('insert into buy (name) values(%s)',(medicine_name,))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    if request.form["m1"] == "m3":
        global em
        ss = cursor.execute('select customer_id from customer where Email = %s',(em,) )
        cid = cursor.fetchall()
        print(cid[0][0])
        cursor.execute('select medicine_id from medicines where name = %s',(medicine_name,) )
        mid = cursor.fetchall()
        
        cursor.execute('INSERT INTO cart (customer_id,medicine_id) VALUES (%s,%s)',(cid[0][0],mid[0][0]))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))

    


@app.route('/signup', methods=['GET'])
def signup_form():
    return render_template('dbms5/sign-in/signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    print("hello")
    username = request.form['nm']
    addrs = request.form['ad']
    phh = request.form['ph']
    ccc = request.form['cc']
    password = str(request.form['ps'])
    
    email = request.form['em']
    global em
    em = email
    
    
    conn = get_db_connection()
    cursor = conn.cursor()
    ss = cursor.execute('select name from customer where Email = %s',(email,) )
    results = cursor.fetchall()
    conn.commit()   
    print(results)
    if not results :
        cursor.execute('INSERT INTO customer (name,address, phone_number, credit_card,Email,passwd) VALUES (%s, %s, %s, %s, %s, %s)', (username,addrs,  phh,ccc, email,password))
        conn.commit()
        conn.close()
        return redirect(url_for("home"))
    return redirect(url_for("signup")) 
    


if __name__ == '__main__':
    create_triggers()
    app.run(debug=True)
