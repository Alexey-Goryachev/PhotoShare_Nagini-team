import re
string = 'tes3t%40example.com_3_1697800873.jpg'
public_id = string.rsplit('.', 1)[0]
print(public_id)