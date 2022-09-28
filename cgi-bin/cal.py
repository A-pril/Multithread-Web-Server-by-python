import sys

# CGI处理模块
# import cgi, cgitb
#
# # 创建 FieldStorage 的实例化
# form = cgi.FieldStorage()
#
# # 获取数据
# a0 = form.getvalue('num1')
# b0 = form.getvalue('num2')
# # print("a0"+a0)
# print("b0"+b0)

ini = sys.argv[1]
# num1=xxx num2=xx
ini = ini.split("&")
a = ini[0].split("=")[1]
b = ini[1].split("=")[1]
# res = ""
# with open("cgi-bin/cal_res.html", "r", encoding="utf-8") as f:
#     for line in f:
#         res += line
# res = res.replace("$a", a)
# res = res.replace("$b", b)
# res = res.replace("$res", str(float(a) + float(b)))
# res = res.replace("$hostname", sys.argv[2])
# res = res.replace("$port", sys.argv[3])
# print(res)

print("<html>\n")
print("<head>\n")
print("<meta charset=\"utf-8\">\n")
print("<title>CGI</title>\n")
print("<style>")
print("h2{width:600px;height:80px;border:solid 10px black;}\n")

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


print("</style>")
print("</head>\n")
print("<body style=\"background-color: 	black\">\n")
# print("table width=\"500\" border=\"0\"\n")
# print("<tr>\n")
# print("<td colspan=\"2\" style=\"background-color:#FFA500;\">\n")
# print("<h1>The result is</h1>\n")
# printf("</td>\n")
# printf("</tr>\n")
#
# printf("<tr>\n")
# printf("<td style=\"background-color:#FFD700;width:100px;\">\n")
# printf("<b>11</b><br>\n")
# printf("HTML<br>\n")
# printf("CSS<br>\n")
# printf("JavaScript\n")
# printf("<td style=\"background-color:#eeeeee;height:200px;width:400px;\">\n")
# printf("22</td>\n")
# printf("</tr>\n")
# printf("<tr>\n")
# printf("<td colspan="2" style=\"background-color:#FFA500;text-align:center;\">\n")
print("<h1><span style=\"color:white\">The Result is : %s + %s = %s</span></h1>\n" % (a, b, str(float(b) + float(a))))
# print("<a href=\"http://127.0.0.1:8888/cal.html\"><h1><li>Return to CALCULATOR PAGE<h1></a>")
print("<h1><input type=\"button\" name=\"btn\" value=\"Return to CALCULATOR PAGE\" onclick=\"javascript:history.back(-1)\" class=\"btn btn-primary\"></h1>")
#print("<img src=\"./1.png\" width=\"700\" height=\"400\">")
#print("<img src=\"./2.png\" width=\"700\" height=\"400\">")
print("</body>\n")
print("</html>\n")