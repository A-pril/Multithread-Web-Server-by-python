import sqlite3
import sys
# 获取查询参数
ini = sys.argv[1]
hostname = sys.argv[2]
port = sys.argv[3]
class_id = ini.split("&")[0].split("=")[1]
class_name = ini.split("&")[1].split("=")[1]
class_name = class_name.replace("+"," ")
teacher_name = ini.split("&")[2].split("=")[1].strip("'")
teacher_name = teacher_name.replace("+"," ")
# 连接数据库
db = sqlite3.connect('data_\Class_data.db')
cursor = db.cursor()
# 生成Select语句
sql1 = ""
sql2 = ""
sql3 = ""
if class_id == "00000":
    sql1 = "SELECT * from class_menu"
else:
    sql1 = "SELECT * from class_menu where ClassID = " + class_id

if class_name == "00000":
    sql2 = "SELECT * from ( "+ sql1 + " )"
else:
    sql2 = "SELECT * from ( "+ sql1 + " ) where ClassName = '" + class_name +"'"

if teacher_name == "00000":
    sql3 = "SELECT * from ( "+ sql2 + " );"
else:
    sql3 = "SELECT * from ( "+ sql2 + " ) where Teacher = '" + teacher_name +"' ;"

cursor.execute(sql3)
data = cursor.fetchall()

# CGI
print("<html>\n")
print("<head>\n")
print("<meta charset=\"utf-8\">\n")
print("<title>Class Data</title>\n")
print("<style>\n")
print("h1 {text-align:center}\n")
print("table{\n")
print("margin: auto;\n")
print("color: white;\n")
print("}\n")

print(".btn{")
print("width: 500px;")
print("height: 50px;")
print("background-color: gainsboro;")
print("line-height: 50px;")
print("font-size: 30px;")
print("color: black;")
print("border-radius: 50px;")
print(".btn:focus{")
print("outline: none;")
print("}")
print(".btn-primary{")
print("background-color: gainsboro;")
print("}")

print("</style>\n")
print("</head>\n")
print("<body  style=\"background-color: 	black\">\n")

print("<h1><span style=\"color:white\">\n")
print("<table border=\"1\"\n")
print("<caption>Class Data</caption>\n" )
print("<tr>\n")
print("<th>ID</th>")
print("<th>NAME</th>")
print("<th>TEACHER</th>")
print("<th>TIME</th>")
print("<th>ROOM</th>")
print("</tr>\n")
for class_data in data:
    print("<tr>\n")
    print("<th>%s</th>" % str(class_data[0]))
    print("<th>%s</th>" % str(class_data[1]))
    print("<th>%s</th>" % str(class_data[2]))
    print("<th>%s</th>" % str(class_data[3]))
    print("<th>%s</th>" % str(class_data[4]))
    print("</tr>\n")
#print("<a href=\"http://127.0.0.1:8888/query.html\"><h1><li>Return to QUERY PAGE<h1></a>")
print("<h1><input type=\"button\" name=\"btn\" value=\"Return to QUERY PAGE\" onclick=\"javascript:history.back(-1)\" class=\"btn btn-primary\"></h1>")
print("</table>\n")

print("</span></h1>\n")
print("</body>\n")
print("</html>\n")