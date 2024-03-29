import socket
from socket import *
import select
import sys
#required flags
exit_flag = False
#cohort details
cohort_tuple = []
#cmd input
input_command = ""

#commands:
TAKE_TNT_CKPT = "take_tentative_check_point"
MK_TNT_CKPT_PRMNT = "make_tentative_check_point_permananent"
UNDO_TNT_CKPT = "undo_tentative_check_point"
PRP_ROLL_MSG = "prepare_to_rollback"
PEER_ROLL_BACK = "roll_back"
DO_NOT_ROLL_BACK = "do_not_roll_back"

#State Variables:
class cohortCustomerClass:
    name = ""
    ipAddress = ""
    currentBalance = 0
    lastLabelrecvd = {}
    firstLabelSent = {}
    lastLabelSent = {}
    oKToTakeChkPoint = "Yes"
    willingToRollBack = "Yes"
    resumeExecution = "Yes"
    rollCohort = []
    chkptCohort = []

    #print function
    def print_data(self):
        print("\n========Customer Details:==========")
        print("Name: ", self.name)
        print("Bank balance: ", self.currentBalance)
        print("lastLabelrecvd: ", self.lastLabelrecvd)
        print("firstLabelSent: ", self.firstLabelSent)
        print("lastLabelSent: ", self.lastLabelSent)
        print("oKToTakeChkPoint: ", self.oKToTakeChkPoint)
        print("willingToRollBack: ", self.willingToRollBack)
        print("resumeExecution: ", self.resumeExecution)
        print("rollCohort: ", self.rollCohort)
        print("chkptCohort: ", self.chkptCohort)

    #intialization function
    def initializeData(self):
        global cohort_tuple
        if cohort_tuple:
            for cohortPeer in cohort_tuple:
                self.firstLabelSent.update({cohortPeer['name'] : 0})
                self.lastLabelrecvd.update({cohortPeer['name'] : 0})
                self.lastLabelSent.update({cohortPeer['name'] : 999})

#Initialize objects 
cohortCustomer = cohortCustomerClass()
tentativeCheckPoint = cohortCustomerClass()
permanentCheckPoint = cohortCustomerClass()

#once the new cohort is created, the cohort details are sent to other peers in the cohort
def sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer):
    print("PEER:: Sending cohort details to peers")
    #update object
    cohortCustomer.initializeData()
    ip_address = cohortCustomer.ipAddress

    for peer in cohort_tuple:
        tupleMsg = str(cohort_tuple)
        peerAddress = peer['ip_address']       
        peerSocket = int(peer['port2'])

        flag = (ip_address != peerAddress) or ((ip_address == peerAddress) and (int(clientPortBank) != int(peer['port1']) and int(clientPortPeer) != peerSocket))
        if(flag):
            clientSocketPeer.sendto(tupleMsg.encode(), (peerAddress, peerSocket))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            if(peerResponse.decode() == "SUCCESS"):
                print("\nPEER:: Cohort details successfully sent to client: ", peer['name'])
            else:
                print("Send-cohort else part")
                continue

#Bank worker function
def bankWorker(input_command, clientPortBank, clientPortPeer):
    global exit_flag  
    global cohort_tuple     

    command_bank = input_command
    #sending command to bank
    print("CLIENT->BANK:: Sending command to bank...")
    clientSocketBank.sendto(command_bank.encode(), (serverName, serverPort))
    print("CLIENT->BANK:: Waiting for response...")
    #waiting for response from bank
    serverResponse, serverAddress = clientSocketBank.recvfrom(2048)
    #decoding response
    rcvd_msg = serverResponse.decode()
    print("CLIENT->BANK:: Response received: ", rcvd_msg)

    msg_cmd = command_bank.split(" ")
    if(msg_cmd[0] == "open" and rcvd_msg == "SUCCESS"):
        #object update on opening bank account
        cohortCustomer.name = msg_cmd[1]
        cohortCustomer.currentBalance = int(msg_cmd[2])
        cohortCustomer.ipAddress = msg_cmd[3]
        print("Customer: " + cohortCustomer.name + "\nBalance: " + str(cohortCustomer.currentBalance))
    #if the new-cohort is created and the response is sent, the details are sent to peers
    if(msg_cmd[0] == "new-cohort" and rcvd_msg != "FAILURE"):
        cohort_tuple = (eval(rcvd_msg))
        sendCohortDetailsToPeers(cohort_tuple, clientPortBank, clientPortPeer)
    #delete cohort 
    if(msg_cmd[0] == "delete-cohort" and rcvd_msg == "SUCCESS"):
        cohort_tuple.clear()
    #exit
    if(msg_cmd[0] == "exit" and rcvd_msg == "SUCCESS"):
        exit_flag = True
        clientSocketBank.close()
    
#peer to peer worker function
def peerWorker(input_command):
    global exit_flag
    if not exit_flag:
        command = input_command.split(" ")
        if((command[0] == "deposit") or (command[0]) == "withdrawal"):
            self_functions(input_command)
        else:
            print("\nCLIENT->PEER:: Inside Peer Function.\n")
            command_peer = input_command
            print("PEER:: command: ", command_peer)
            #transfer money
            if (command[0] == "transfer"):
                inCohortFlag = False
                for tuple in cohort_tuple:
                    if tuple["name"] == command[2]:
                        inCohortFlag = True
                        recieverTuple = tuple
                        if(int(command[1]) > cohortCustomer.currentBalance):
                            print("\nPEER:: Transfer cannot be performed due to insufficient funds")
                            return
                        else:
                            print("\nPEER:: Transfer initiated.")
                            #object update
                            cohortCustomer.currentBalance = cohortCustomer.currentBalance - int(command[1])
                            cohortCustomer.firstLabelSent[command[2]] += 1
                            receiverMessage = 'transfer' + ' ' + command[1] + ' ' + cohortCustomer.name + ' ' + str(cohortCustomer.firstLabelSent[command[2]])
                            print("PEER:: Command to transfer: ", receiverMessage)
                            cohortCustomer.print_data()
                            clientSocketPeer.sendto(receiverMessage.encode(),(recieverTuple['ip_address'], int(recieverTuple['port2'])))
                if(inCohortFlag != True):
                    print("PEER:: Receiver is not in your cohort.")
            #lost-transfer
            elif(command[0] == "lost-transfer"):
                print("\nPEER:: Simulating a lost transfer...")
                inCohortFlag = False
                for tuple in cohort_tuple:
                    if tuple["name"] == command[2]:
                        inCohortFlag = True
                        recieverTuple = tuple
                        if(int(command[1]) > cohortCustomer.currentBalance):
                            print("PEER:: Transfer cannot be performed due to insufficient funds")
                            return
                        else:
                            print("PEER:: Transfer initiated.")
                            #object update
                            cohortCustomer.currentBalance = cohortCustomer.currentBalance - int(command[1])
                            cohortCustomer.firstLabelSent[command[2]] += 1
                            cohortCustomer.print_data()
                            print("\nPEER:: Transfer Lost")
                                
                if(inCohortFlag != True):
                    print("PEER:: Receiver is not in your cohort.")
            
            elif(command[0] == "checkpoint"):
                checkpoint()
            elif(command[0] == "rollback"):
                rollback()

            else:
                clientSocketPeer.sendto(command_peer.encode(), (serverName, serverPort))
                peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
                rcvd_msg = peerResponse.decode()
                print(rcvd_msg)

#self functions:
def self_functions(input_command):
    global exit_flag
    if not exit_flag:
        print("PEER:: Functions performing at customer end.")
        cmnd = input_command.split(" ")
        if(cmnd[0] == "deposit"):
            print("PEER:: Performing a deposit of " + cmnd[1] + " USD.")
            #object update
            cohortCustomer.currentBalance = cohortCustomer.currentBalance + int(cmnd[1])
            print("PEER:: Updated bank balance: ", cohortCustomer.currentBalance)
        elif(cmnd[0] == "withdrawal"):
            if(cohortCustomer.currentBalance < int(cmnd[1])):
                print("PEER:: Withdrawal cannot be performed due to insufficient funds.")
                print("PEER:: Bank balance: ", cohortCustomer.currentBalance)
            else:
                print("PEER:: Withdrawal of amount " + cmnd[1] + " USD.")
                #object update
                cohortCustomer.currentBalance = cohortCustomer.currentBalance - int(cmnd[1])
                print("PEER:: Updated bank balance: ", cohortCustomer.currentBalance)
        else:
            print("PEER:: Wrong command.")

#checkpoint algorithm
def checkpoint():
    global exit_flag
    global cohort_tuple

    if not exit_flag:
        print("\nPEER:: Initiating checkpoint algortihm...")
        #sender taking a tentative checkpoint
        local_tentative_chkpt()
        tnt_yes = True
        print(f"PEER:: Customers in checkpoint cohort: {cohortCustomer.chkptCohort} \n")
        #sending to take tentative checkpoint
        for cust in cohortCustomer.chkptCohort:
            cmd = TAKE_TNT_CKPT + ' ' + cohortCustomer.name + ' ' + str(cohortCustomer.lastLabelrecvd[cust])
            receiverTuple = {}
            for tuple in cohort_tuple:
                if(tuple['name'] == cust):
                    receiverTuple = tuple
                    break
            print(f"PEER:: Sending '{cmd}' to '{cust}'\n")
            clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            rcvd_msg = peerResponse.decode().split(' ')
            print(f"PEER:: Customer '{cust}' is ready to take checkpoint -> '{rcvd_msg[1]}'")
            if(rcvd_msg[0] == cust) and (rcvd_msg[1] == 'No'):
                tnt_yes = False
                break
        #once we receive yes from all the customers, we make the tentative checkpoint to permanent
        if(tnt_yes):
            print("PEER:: Making a permanent checkpoint.")
            chkptchrt = cohortCustomer.chkptCohort
            #sender taking a permanent checkpoint
            local_permanent_chkpt()
            for cust in chkptchrt:
                cmd = MK_TNT_CKPT_PRMNT
                receiverTuple = {}
                for tuple in cohort_tuple:
                    if(tuple['name'] == cust):
                        receiverTuple = tuple
                        break
                print(f"PEER:: Sending a '{cmd}' to '{cust}'")
                clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))
            cohortCustomer.chkptCohort.clear()
            cohortCustomer.print_data()
            tentativeCheckPoint.chkptCohort.clear()
        #if we dont get yes from all customers, we send undo checkpoint
        else:
             for cust in cohortCustomer.chkptCohort:
                cmd = UNDO_TNT_CKPT
                receiverTuple = {}
                for tuple in cohort_tuple:
                    if(tuple['name'] == cust):
                        receiverTuple = tuple
                        break
                print(f"PEER:: Sending a '{cmd}' to '{cust}'")
                clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))

#take tentative checkpoint
def take_tentative_chkpt(senderPeer, lastReceieved):
    print("PEER:: Inside taking tentative check point")
    print("PEER:: Take tentative Checkpoint received from customer : ", senderPeer)

    #local tentative checkpoint at receiver
    if ((cohortCustomer.oKToTakeChkPoint == "Yes") and (lastReceieved >= cohortCustomer.firstLabelSent[senderPeer] > 0)):
        print("PEER:: Taking a tentative check point.")
        local_tentative_chkpt()
        tentativeCheckPoint.print_data()
        tnt_yes = True
        #sending tentative checkpoint to receiver
        for cust in cohortCustomer.chkptCohort:
            cmd = TAKE_TNT_CKPT + ' ' + cohortCustomer.name + ' ' + str(cohortCustomer.lastLabelrecvd[cust])
            receiverTuple = {}
            for tuple in cohort_tuple:
                if(tuple['name'] == cust):
                    receiverTuple = tuple
                    break
            clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            rcvd_msg = peerResponse.decode().split(' ')
            if(rcvd_msg[0] == cust) and (rcvd_msg[1] == 'No'):
                tnt_yes = False
                break
        #if all process send yes, we send okay to take checkpoint else no
        if(tnt_yes):
            cohortCustomer.oKToTakeChkPoint = "Yes"
        else:
            cohortCustomer.oKToTakeChkPoint = "No"
    
    receiverTuple ={}
    for tuple in cohort_tuple:
        if(tuple['name'] == senderPeer):
            receiverTuple = tuple
            break
    cmd = cohortCustomer.name + ' ' + cohortCustomer.oKToTakeChkPoint
    print(f"PEER:: Sending reply command '{cmd}'")
    clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))

#helper function
def local_tentative_chkpt():
    print("Saving to tentative checkpoint.")
    tentativeCheckPoint.name = cohortCustomer.name
    tentativeCheckPoint.currentBalance = cohortCustomer.currentBalance
    tentativeCheckPoint.ipAddress = cohortCustomer.ipAddress
    tentativeCheckPoint.willingToRollBack = cohortCustomer.willingToRollBack
    tentativeCheckPoint.resumeExecution = cohortCustomer.resumeExecution
    tentativeCheckPoint.oKToTakeChkPoint = cohortCustomer.oKToTakeChkPoint
    return

#helper function
def local_permanent_chkpt():
    global cohort_tuple
    print("\nPEER:: Making a permanent Checkpoint.")
    
    for key in cohortCustomer.firstLabelSent:
        cohortCustomer.lastLabelSent[key] = cohortCustomer.firstLabelSent[key]

    for key in tentativeCheckPoint.firstLabelSent:
        tentativeCheckPoint.lastLabelSent[key] = tentativeCheckPoint.firstLabelSent[key]

    permanentCheckPoint.name = tentativeCheckPoint.name
    permanentCheckPoint.currentBalance = tentativeCheckPoint.currentBalance
    permanentCheckPoint.ipAddress = tentativeCheckPoint.ipAddress
    permanentCheckPoint.willingToRollBack = tentativeCheckPoint.willingToRollBack
    permanentCheckPoint.resumeExecution = tentativeCheckPoint.resumeExecution
    permanentCheckPoint.oKToTakeChkPoint = tentativeCheckPoint.oKToTakeChkPoint

    if cohort_tuple:
        for cohortPeer in cohort_tuple:
            permanentCheckPoint.firstLabelSent.update({cohortPeer['name'] : 0})
            permanentCheckPoint.lastLabelrecvd.update({cohortPeer['name'] : 0})
            permanentCheckPoint.lastLabelSent.update({cohortPeer['name'] : 999})

    permanentCheckPoint.print_data()
    print("\n")
    return

#making permanent checkpoint
def make_permanent_chkpt():
    print("PEER:: Inside permanent checkpoint")
    local_permanent_chkpt()
    for cust in cohortCustomer.chkptCohort:
        receiverTuple = {}
        cmd = MK_TNT_CKPT_PRMNT
        for tuple in cohort_tuple:
            if(tuple['name'] == cust):
                receiverTuple = tuple
                break
        clientSocketPeer.sendto(cmd.encode(), (receiverTuple['ip_address'], int(receiverTuple['port2'])))

#undo tentative checkpoint
def undo_tentative_chkpt():
    print("Inside undo tentative checkpoint")

#roll back start
def rollback():
    print("PEER:: Inside roll backfunction.")
    global exit_flag
    global cohort_tuple
    if not exit_flag:
        print("\nPEER:: Initiating Rollback algorithm...")
        rollback_flag = True
        cohortCustomer.rollCohort = cohort_tuple
        print("DEBUG:: cohort tuple : ", cohortCustomer.rollCohort)
        for peer in cohortCustomer.rollCohort:
            if(peer['name'] == cohortCustomer.name):
                continue
            cmd = (PRP_ROLL_MSG+' '+cohortCustomer.name+' '+str(cohortCustomer.lastLabelSent[peer['name']])) 
            print(f"\nPEER:: Sending '{cmd}' to '{peer['name']}'.")         
            clientSocketPeer.sendto(cmd.encode(),(peer['ip_address'],int(peer['port2'])))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            rcvd_msg = peerResponse.decode().split(' ')
            if (rcvd_msg[1] == 'No'):
                print("PEER:: Received no for Rollback from -> ", rcvd_msg[0])
                rollback_flag = False           
                break
        if (rollback_flag):
            loc_roll_back()
            for peer in cohortCustomer.rollCohort:
                if(peer['name'] == cohortCustomer.name):
                    continue
                else:
                    clientSocketPeer.sendto(PEER_ROLL_BACK.encode(),(peer['ip_address'],int(peer['port2'])))
            cohortCustomer.rollCohort = []
            cohortCustomer.chkptCohort = []
            print("\nPEER:: Data after rollback.")
            cohortCustomer.print_data()
        else:
            for peer in cohortCustomer.rollCohort:
                if(peer['name'] == cohortCustomer.name):
                    continue
                else:
                    clientSocketPeer.sendto(DO_NOT_ROLL_BACK.encode(),(peer['ip_address'],int(peer['port2'])))     

#prepare to rollback function
def prepare_to_rollback(senderPeer, lastSent):
    print("\nPEER:: Preparing to rollback...")
    if ((cohortCustomer.willingToRollBack == "Yes") and (cohortCustomer.lastLabelrecvd[senderPeer] > int(lastSent)) and (cohortCustomer.resumeExecution=='Yes')):
        cohortCustomer.resumeExecution = "No"
        print("DEBUG:: here I am")
        for peer in cohortCustomer.rollCohort:
            if(peer['name'] == cohortCustomer.name):
                continue   
            cmd = (PRP_ROLL_MSG+' '+cohortCustomer.name+' '+str(cohortCustomer.lastLabelrecvd[peer])) 
            print(f"PEER:: Sending {cmd} to customer {peer['name']}.")
            clientSocketPeer.sendto(cmd.encode(),(peer['ip_address'],int(peer['port2'])))
            peerResponse, peerAddress = clientSocketPeer.recvfrom(2048)
            rcvd_msg = peerResponse.decode().split(' ')
            if (rcvd_msg[1] == 'No'):
                rollback_flag = False           
                break

        if (rollback_flag):
            cohortCustomer.willingToRollBack = "Yes"
            
        else:
            cohortCustomer.willingToRollBack = "No"
        
    cmnd = cohortCustomer.name + ' ' + cohortCustomer.willingToRollBack
    print(f"PEER:: Sending {cmnd} to {senderPeer}.")
    receiverTuple ={}
    for tuple in cohort_tuple:
        if(tuple['name'] == senderPeer):
            receiverTuple = tuple
            break       
    clientSocketPeer.sendto(cmnd.encode(),(receiverTuple['ip_address'], int(receiverTuple['port2'])))

#helper fucntion
def loc_roll_back():
    global cohort_tuple
    cohortCustomer.name = permanentCheckPoint.name
    cohortCustomer.currentBalance = permanentCheckPoint.currentBalance
    cohortCustomer.ipAddress = permanentCheckPoint.ipAddress
    cohortCustomer.willingToRollBack = permanentCheckPoint.willingToRollBack
    cohortCustomer.resumeExecution = permanentCheckPoint.resumeExecution
    cohortCustomer.oKToTakeChkPoint = permanentCheckPoint.oKToTakeChkPoint
    if cohort_tuple:
        for cohortPeer in cohort_tuple:
            cohortCustomer.firstLabelSent.update({cohortPeer['name'] : 0})
            cohortCustomer.lastLabelrecvd.update({cohortPeer['name'] : 0})
            cohortCustomer.lastLabelSent.update({cohortPeer['name'] : 999})

#rolling back function
def peer_roll_back():
    loc_roll_back()
    for peer in cohortCustomer.rollCohort:
        if(peer['name'] == cohortCustomer.name):
            continue 
        clientSocketPeer.sendto(PEER_ROLL_BACK.encode(),(peer['ip_address'],int(peer['port2'])))
    print("\nPEER:: Data after rollback.")
    cohortCustomer.rollCohort.clear()
    cohortCustomer.print_data()

#do not rollback function
def do_not_roll_back():
    cohortCustomer.resumeExecution = "Yes"
    print("PEER:: Not rolling back.")
    for peer in cohortCustomer.rollCohort:
        if(peer['name'] == cohortCustomer.name):
            continue 
        clientSocketPeer.sendto(DO_NOT_ROLL_BACK.encode(),(peer['ip_address'],int(peer['port2'])))

#main function
if __name__ == "__main__":
    print("********** CHECKPOINT: Customer Process **********")
    serverName = input("\nCLIENT:: Enter the IP address of the Bank Server Process: ")
    serverPort = int(input("CLIENT:: Enter the Port number of the Bank Server Process: "))

    #customer port for communicating with bank
    while (True):
        clientPortBank = int(input("\nCLIENT:: Enter a port number for Bank communication b/w 8500 - 8999: "))
        if 8500 <= clientPortBank <=8999:
            break
        else:
            print("CLIENT:: Wrong port number")

    #customer port for communicating with peer
    while (True):
        clientPortPeer = int(input("CLIENT:: Enter a port number for Peer communication b/w 8500 - 8999: "))
        if 8500 <= clientPortPeer <=8999 and clientPortPeer != clientPortBank:
            break
        else:
            print("CLIENT:: Wrong port number")
    
    clientSocketBank = socket(AF_INET, SOCK_DGRAM)
    clientSocketBank.bind(('', clientPortBank))
    print("CLIENT:: Socket to communicate with Bank created successfully.")
    clientSocketPeer = socket(AF_INET, SOCK_DGRAM)
    clientSocketPeer.bind(('', clientPortPeer))
    print("CLIENT:: Socket to communicate with Peer created successfully.")
    
    sockets = []
    sockets.append(clientSocketBank)
    sockets.append(clientSocketPeer)

    #checking each socket if the data is present at the socket
    while not exit_flag:
        print("\nCLIENT:: Enter the command to send to bank: ")
        readable, writable, exceptional = select.select(sockets + [sys.stdin], [], [])

        #foreach socket 
        for sock in readable:
            #if there is any data
            if sock is sys.stdin:
                user_input_command = sys.stdin.readline().strip()
                cmd = user_input_command.split(" ")

                if(cmd[0] == "open" or cmd[0] == "new-cohort" or cmd[0] == "delete-cohort" or cmd[0] == "exit"):
                    bankWorker(user_input_command, clientPortBank, clientPortPeer)
                elif(cmd[0] == "deposit" or cmd[0] == "withdrawal" or cmd[0] == "transfer" or cmd[0] == "lost-transfer" or cmd[0] == "checkpoint" or cmd[0] == "rollback"):
                    peerWorker(user_input_command)
                else:
                    print("CLIENT:: Wrong command")

            if sock is clientSocketBank:
                msg,ret_address = clientSocketBank.recvfrom(1024)
                if (msg.decode() == "delete-cohort"):
                    print("\nCLIENT:: Received 'delete-cohort' command from bank.")

                    print("\nCLIENT:: Current cohort (before deleting): ", cohort_tuple)
                    cohort_tuple.clear()
                    cohortCustomer.chkptCohort.clear()
                    cohortCustomer.rollCohort.clear()

                    print("\nCLIENT:: Cohort tuple (after deleting): ", cohort_tuple)
                    print("CLIENT:: Cohort deleted successfully.")
                    clientSocketBank.sendto("SUCCESS".encode(),ret_address)

            if sock is clientSocketPeer:
                msg,ret_address = clientSocketPeer.recvfrom(1024)
                msgData = msg.decode().split(' ')
                if (msgData[0] == 'transfer'):
                    print(f"\nPEER:: Received a transfer of amount {msgData[1]} USD from customer {msgData[2]}")
                    if (cohortCustomer.resumeExecution == "Yes"):
                        cohortCustomer.currentBalance = cohortCustomer.currentBalance + int(msgData[1])
                        if(msgData[2] not in cohortCustomer.chkptCohort):
                            cohortCustomer.chkptCohort.append(msgData[2])
                        if(int(msgData[3]) - cohortCustomer.lastLabelrecvd[msgData[2]] > 1):
                            cohortCustomer.oKToTakeChkPoint = "No"
                        cohortCustomer.lastLabelrecvd[msgData[2]] += 1
                        print("PEER:: Updated customer Details")
                        cohortCustomer.print_data()
                    else:
                        print("PEER:: Further transfers are not possible as Resume to execution is 'No'.")
                
                elif(msgData[0] == TAKE_TNT_CKPT):
                    take_tentative_chkpt(msgData[1], int(msgData[2]))
                
                elif(msgData[0] == MK_TNT_CKPT_PRMNT):
                    make_permanent_chkpt()
                
                elif(msgData[0] == UNDO_TNT_CKPT):
                    undo_tentative_chkpt()

                elif(msgData[0] == PRP_ROLL_MSG):
                    prepare_to_rollback(msgData[1],msgData[2])
                
                elif(msgData[0] == PEER_ROLL_BACK):
                    peer_roll_back()
                
                elif(msgData[0] == DO_NOT_ROLL_BACK):
                    do_not_roll_back()

                else:
                    print("\nCLIENT:: Received Cohort tuple")
                    cohort_tuple = eval(msg.decode())
                    print("CLIENT:: Current Cohort: \n", cohort_tuple)
                    cohortCustomer.initializeData()
                    clientSocketBank.sendto("SUCCESS".encode(),ret_address)
        
    print("\nCLIENT:: Exiting bank application")
    clientSocketPeer.close()