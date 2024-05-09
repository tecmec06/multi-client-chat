import tkinter as tk
from tkinter import messagebox
import socket
import threading
from tkinter.filedialog import askopenfilename
import os

window = tk.Tk()
window.title("Client")
username = " "


topFrame = tk.Frame(window)
lblName = tk.Label(topFrame, text = "Name:").pack(side=tk.LEFT)
entName = tk.Entry(topFrame)
entName.pack(side=tk.LEFT)
btnConnect = tk.Button(topFrame, text="Connect", command=lambda : connect())
btnConnect.pack(side=tk.LEFT)
#btnConnect.bind('<Button-1>', connect)
topFrame.pack(side=tk.TOP)

displayFrame = tk.Frame(window)
lblLine = tk.Label(displayFrame, text="*********************************************************************").pack()
scrollBar = tk.Scrollbar(displayFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(displayFrame, height=20, width=55)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
tkDisplay.tag_config("tag_your_message", foreground="blue")
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
displayFrame.pack(side=tk.TOP)


bottomFrame = tk.Frame(window)
tkMessage = tk.Text(bottomFrame, height=2, width=35)
tkMessage.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
tkMessage.config(highlightbackground="grey", state="disabled")
tkMessage.bind("<Return>", (lambda event: getChatMessage(tkMessage.get("1.0", tk.END))))
btnSend = tk.Button(bottomFrame, height=2, text="Send Message", command=lambda : getChatMessage(tkMessage.get("1.0", tk.END)))
btnSend.pack(side=tk.LEFT)
btnFSend = tk.Button(bottomFrame, height=2, text="Send File", command=lambda :send_file() )
btnFSend.pack(side=tk.LEFT)
bottomFrame.pack(side=tk.BOTTOM)

bottomFrame2 = tk.Frame(window)
lblLine1 = tk.Label(bottomFrame2, text="To: ")
lblLine1.pack(side=tk.LEFT)
tkMessage2 = tk.Text(bottomFrame2, height=2, width=35)
tkMessage2.pack(side=tk.LEFT, padx=(5, 13), pady=(5, 10))
bottomFrame2.pack(side=tk.BOTTOM)


def connect():
    global username, client
    if len(entName.get()) < 1:
        tk.messagebox.showerror(title="ERROR!!!", message="You MUST enter your first name!")
    else:
        username = entName.get()
        connect_to_server(username)



client = None
HOST_ADDR = 'localhost'
HOST_PORT = 1234

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) 

        entName.config(state=tk.DISABLED)
        btnConnect.config(state=tk.DISABLED)
        tkMessage.config(state=tk.NORMAL)

        threading._start_new_thread(receive_message_from_server, (client, " "))
    except Exception as e:
        tk.messagebox.showerror(title="ERROR!!!", message="Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")

def send_file():
    filename = askopenfilename()
    file = open(filename, "rb")
    
    file_size = os.path.getsize(filename)
    fname = filename.split('/')
    nname = fname[len(fname)-1]
    client.send(("ff,"+ str(file_size) + "," + str(nname)).encode())
    data = file.read()
    if not data:
        return
    while data:
        client.send(data)
        data = file.read()
    file.close()
    

def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: 
            break
        texts = tkDisplay.get("1.0", tk.END).strip()
        tkDisplay.config(state=tk.NORMAL)
        if len(texts) < 1:
            tkDisplay.insert(tk.END, from_server)
        else:
            tkDisplay.insert(tk.END, "\n\n"+ from_server)

        tkDisplay.config(state=tk.DISABLED)
        tkDisplay.see(tk.END)


    sck.close()
    window.destroy()


def getChatMessage(msg):

    msg = msg.replace('\n', '')
    texts = tkDisplay.get("1.0", tk.END).strip()
    to_user = tkMessage2.get("1.0", tk.END).strip()
    print(to_user)

    tkDisplay.config(state=tk.NORMAL)
    if len(texts) < 1:
        tkDisplay.insert(tk.END, "You->" + msg, "tag_your_message") # no line
    else:
        tkDisplay.insert(tk.END, "\n\n" + "You->" + msg, "tag_your_message")

    tkDisplay.config(state=tk.DISABLED)

    send_mssage_to_server(msg, to_user)

    tkDisplay.see(tk.END)
    tkMessage.delete('1.0', tk.END)


def send_mssage_to_server(msg, to_user):
    client_msg = str(msg)
    client.send(("," + to_user + "," + client_msg).encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")


window.mainloop()