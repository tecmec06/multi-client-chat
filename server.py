import tkinter as tk
import socket
import threading
import select


window = tk.Tk()
window.title("Sever")

topFrame = tk.Frame(window)
btnStart = tk.Button(topFrame, text="Connect", command=lambda : start_server())
btnStart.pack(side=tk.LEFT)
btnStop = tk.Button(topFrame, text="Stop", command=lambda : stop_server(), state=tk.DISABLED)
btnStop.pack(side=tk.LEFT)
topFrame.pack(side=tk.TOP, pady=(5, 0))

middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text = "Host: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text = "Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

clientFrame = tk.Frame(window)
lblLine = tk.Label(clientFrame, text="**********Client List**********").pack()
scrollBar = tk.Scrollbar(clientFrame)
scrollBar.pack(side=tk.RIGHT, fill=tk.Y)
tkDisplay = tk.Text(clientFrame, height=15, width=30)
tkDisplay.pack(side=tk.LEFT, fill=tk.Y, padx=(5, 0))
scrollBar.config(command=tkDisplay.yview)
tkDisplay.config(yscrollcommand=scrollBar.set, background="#F4F6F7", highlightbackground="grey", state="disabled")
clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))


server = None
HOST_ADDR = 'localhost'
HOST_PORT = 1234
client_name = " "
clients = []
clients_names = []


def start_server():
    global server, HOST_ADDR, HOST_PORT 
    btnStart.config(state=tk.DISABLED)
    btnStop.config(state=tk.NORMAL)

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Host: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)


def stop_server():
    global server
    btnStart.config(state=tk.NORMAL)
    btnStop.config(state=tk.DISABLED)
    server.close()


def accept_clients(the_server, y):
    while True:
        client, addr = the_server.accept()
        clients.append(client)

        threading._start_new_thread(send_receive_client_message, (client, addr))


def send_receive_client_message(client_connection, client_ip_addr):
    global server, client_name, clients, clients_addr
    client_msg = " "

    client_name  = client_connection.recv(4096).decode()
    welcome_msg = "Welcome " + client_name + ". Use 'exit' to quit"
    client_connection.send(welcome_msg.encode())

    clients_names.append(client_name)

    update_client_names_display(clients_names)  


    while True:
        data = client_connection.recv(1024).decode()
        dsplit = data.split(',')
        if dsplit[0] == 'ff':
            try:
                
                file_size = dsplit[1]

                dataw = client_connection.recv(int(file_size))
                if not dataw:
                    continue
                print(dsplit[2])
                file = open(dsplit[2], "wb")
                while dataw:
                    if not dataw:
                        print('Received successfully! New filename is:', dsplit[2])
                        file.close()
                        break
                    else:
                        file.write(dataw)
                        dataw = client_connection.recv(int(file_size))
                
            except socket.error as err:
                print("Error Msg: " + str(err))
                file.close()
                pass
        else:
            if not data: break
            if dsplit[2] == "exit": break

            client_msg = dsplit[2]
            if dsplit[1] != "":
                idx = get_client_index(clients_names, dsplit[1])
                # print(clients)
                # print(clients_names)
                sending_client_name = clients_names[idx]
                # for c in range(len(clients)):
                #     if c == idx:
                server_msg = str(sending_client_name + "->" + client_msg)
                clients[idx].send(server_msg.encode())
            else:
                    
                idx = get_client_index(clients, client_connection)
                sending_client_name = clients_names[idx]

                for c in clients:
                    if c != client_connection:
                        server_msg = str(sending_client_name + "->" + client_msg)
                        c.send(server_msg.encode())

    idx = get_client_index(clients, client_connection)
    del clients_names[idx]
    del clients[idx]
    server_msg = "BYE!"
    client_connection.send(server_msg.encode())
    client_connection.close()

    update_client_names_display(clients_names)  


def get_client_index(client_list, curr_client):
    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1
    return idx


def update_client_names_display(name_list):
    tkDisplay.config(state=tk.NORMAL)
    tkDisplay.delete('1.0', tk.END)

    for c in name_list:
        tkDisplay.insert(tk.END, c+"\n")
    tkDisplay.config(state=tk.DISABLED)


window.mainloop()