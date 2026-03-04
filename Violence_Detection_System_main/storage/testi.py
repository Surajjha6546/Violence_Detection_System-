D:\Violence_Detection_System>import sqlite3
'import' is not recognized as an internal or external command,
operable program or batch file.

D:\Violence_Detection_System>
D:\Violence_Detection_System>conn = sqlite3.connect("storage/logs.db")
'conn' is not recognized as an internal or external command,
operable program or batch file.

D:\Violence_Detection_System>cursor = conn.cursor()
'cursor' is not recognized as an internal or external command,
operable program or batch file.

D:\Violence_Detection_System>
D:\Violence_Detection_System>rows = cursor.execute("SELECT * FROM incidents").fetchall()
'rows' is not recognized as an internal or external command,
operable program or batch file.

D:\Violence_Detection_System>print(rows)
Unable to initialize device PRN

D:\Violence_Detection_System>
D:\Violence_Detection_System>conn.close()
'conn.close' is not recognized as an internal or external command,
operable program or batch file.
