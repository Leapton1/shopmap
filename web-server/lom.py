from flask import Flask, render_template, jsonify, request, url_for, redirect
import psycopg2
import json
import time
import os

app = Flask("dom")

table3=[]
try:
    # conn=psycopg2.connect(host='localhost',database='inventory',user='inventory',password='inventory')
    conn=psycopg2.connect(host='dpg-cf80romn6mplr40lfeeg-a',database='inventory_na16',user='inventory',password='n1QrdZzbDjcRFhHGaPr5hQ5gLeV6DQQv')
    setup=True
    cur=conn.cursor()
except:
    print("no")
    setup=False


def safe(s):
    return s.replace("'","''")

def update():
    global table3
#   cur.execute("select inventory.id,products.name,x,y from inventory "+
#                "join products on product_id=products.id "+
#                "join shops on shops.id=shop_id "+
#                "where shops.name='Generic store';")
    cur.execute("select id,name,x,y from inventory;")
    table1=list(cur.fetchall())
    print(table1)
    table2=[]

    cur.execute('select max(x) from inventory')
    maxcoords=[cur.fetchall()[0][0]]

    cur.execute('select max(y) from inventory')
    maxcoords.append(cur.fetchall()[0][0])
    print(maxcoords)
    
    for i in range(0,maxcoords[0]):
        table2.append([])
        for i2 in range(0,maxcoords[1]):
            table2[i].append([])
    
    for i in range(0,len(table1)):
        table2[table1[i][2]-1][table1[i][3]-1].append(table1[i][1])
    
    print(table2)
    table3=[]

    for i in range(0,len(table2)):
        table3.append([])
        for i2 in range(0,len(table2[i])):
            table3[i].append([table2[i][i2]])
            if len(table2[i][i2])==0:
                table3[i][i2].append(2)
            else:
                table3[i][i2].append(0)
            table3[i][i2].append(False)
        
    print(table3)
    time.sleep(2)
    
if setup:
    update()
        
@app.route("/")
def hello_world():
    if setup:
        return render_template('something.html')
    else:
        return render_template('warning.html')

@app.route("/init", methods = ['GET'])
def initer():
    return render_template('initialiser.html')

#@app.route("/init", methods = ['POST'])
#def initerpost():
#    print(request.form.get("password"))
#    conn=psycopg2.connect(host='localhost',database='postgres',user='postgres',password=request.form.get("password"))
#    return redirect("/admin", code=302)


@app.route("/admin")
def hello_admin():
    if setup:
        return render_template('something_else.html')
    else:
        return render_template('warning.html')

@app.route('/api')
def api():
    return jsonify(table3)

@app.route('/postman', methods = ['POST'])
def postman():
    global conn
    pat=request.get_json()
    print(pat)
    
    if pat[2]=='add':
        
        if pat[1][0]>=len(table3):
            for i in range(0,pat[1][0]-len(table3)+1):
                table3.append([])
                addend=len(table3)-1
                for i in range(0,len(table3[0])):
                    table3[addend].append([[],2,False])
                print(table3)
                
        if pat[1][1]>=len(table3[0]):
            for i in range(0,pat[1][1]-len(table3[0])+1):
                for i2 in range(0,len(table3)):
                    table3[i2].append([[],2,False])
    
        table3[pat[1][0]][pat[1][1]][0].append(pat[0])
        table3[pat[1][0]][pat[1][1]][1]=0
        print(table3)
        cur=conn.cursor()
        cur.execute("insert into inventory(x,y,shop_id,product_id,name) values (%s,"+safe(str(pat[1][1]+1))+",1,1,'"+safe(pat[0])+"');", str(pat[1][0]+1))
        conn.commit()
        cur.close()
    elif pat[2]=='remove':
        
        check=False;
        print(table3[pat[1][0]][pat[1][1]][0]);
        for i in range(0,len(table3[pat[1][0]][pat[1][1]][0])):
            if pat[0]==table3[pat[1][0]][pat[1][1]][0][i]:
                print(pat[0],i)
                marker=i
                check=True
        if check==True:
            print("e");
            table3[pat[1][0]][pat[1][1]][0].pop(marker);
            
        if(len(table3[pat[1][0]][pat[1][1]][0])==0):
            table3[pat[1][0]][pat[1][1]][1]=2;
            
        check=False
        while check==False:
            for i in range(0,len(table3)):
                if table3[i][len(table3[0])-1][1]==0:
                    check=True
            if check==False:
                for i in range(0,len(table3)):
                    table3[i].pop()
                    
        check=False
        while check==False:
            for i in range(0,len(table3[0])):
                if table3[len(table3)-1][i][1]==0:
                    check=True
            if check==False:
                    table3.pop()
        
            
        cur=conn.cursor()
        cur.execute("DELETE FROM inventory WHERE name='"+safe(pat[0])+"' AND x="+safe(str(pat[1][0]+1))+" AND y="+safe(str(pat[1][1]+1))+";")
        conn.commit()
        cur.close()
        
    return jsonify(['hello'])

@app.route("/hello")
def hello_objects():
    return "<p>Hello, objects!</p>"
  
#app.run()

port=os.getenv('PORT') or 80

app.run(host='0.0.0.0', port=port)