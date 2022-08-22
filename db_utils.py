import sqlite3

conn = sqlite3.connect("data.db", check_same_thread=False)
c = conn.cursor()


# Table
def create_uploaded_filestable():
    c.execute(
        "CREATE TABLE IF NOT EXISTS filestable(filename TEXT, filetype TEXT, filesize TEXT, uploadDate TIMESTAMP)"
    )


#  Adding details
def add_file_details(filename, filetype, filesize, uploadDate):
    c.execute(
        "INSERT INTO filestable(filename, filetype, filesize, uploadDate) VALUES (?,?,?,?)",
        (filename, filetype, filesize, uploadDate),
    )
    conn.commit()


# View details
def view_all_data():
    c.execute("SELECT * FROM filestable")
    data = c.fetchall()
    return data
