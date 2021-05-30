'''
Answers:
	flag:  FLAG{545f274804}
	ASCII: 70 76 65 71 123 53 52 53 102 50 55 52 56 48 52 125
	BIN:   0b1000110 0b1001100 0b1000001 0b1000111 0b1111011 0b110101 0b110100 0b110101 0b1100110 0b110010 0b110111 0b110100 0b111000 0b110000 0b110100 0b1111101
	HEX:   0x46 0x4c 0x41 0x47 0x7b 0x35 0x34 0x35 0x66 0x32 0x37 0x34 0x38 0x30 0x34 0x7d
	OCTAL: 0o106 0o114 0o101 0o107 0o173 0o65 0o64 0o65 0o146 0o62 0o67 0o64 0o70 0o60 0o64 0o175
'''
import socketserver
import time
import sys

class challenge():
	##Converts ascii to text
	def asciiToText(  self ):
		##Controls while loop
		correct = 0
		## user guess varailbe
		flagGuess = ''
		##Correct variable
		flag = 'FLAG{545f274804}'
		## send to user to convert from ascii into the flag
		self.request.sendall( bytes ( "Convert the ASCII into the flag!\n", "utf-8" ) )

		##While correct does not equal 1 continue
		while correct != 1:
			## save the users guess into flagGuess
			flagGuess = self.request.recv(1024).strip()
			flagGuess = flagGuess.decode( "utf-8" )
			##If guess is equal to answer
			if flag == flagGuess:
				##Set correct to 1
				correct = 1
				##Tell user they got it right
				self.request.sendall( bytes ( "You've decoded the flag!\n", "utf-8" ) ) 
			##else if guess is wrong
			else:
				##send to the user that the flag is wrong, format of answer
				self.request.sendall( bytes ( "That is incorrect, format: FLAG{123....}\n", "utf-8" ) )
				##set the flagGuess variable to null
				flagGuess = ''

	##converts from binary to ASCII
	def octalToAscii(  self ):
		##correct ot control client right/wrong
		correct = 0
		##user guess variable
		asciiGuess = ''
		##Correct string
		asci = '70 76 65 71 123 53 52 53 102 50 55 52 56 48 52 125'
		##Client message from server
		self.request.sendall( bytes ( "Convert the octal into ASCII (Decimal Notation)!\n", "utf-8" ) )
		##while correct doesnt equal 1 continue
		while correct != 1:
			##get user guess in asciiGuess
			asciiGuess = self.request.recv(1024).strip()
			asciiGuess = asciiGuess.decode( "utf-8" )
			## if user guess is right
			if asci == asciiGuess:
				##set correct to 1
				correct = 1
				##send alert to user that it is correct
				self.request.sendall( bytes ( "That is correct!\nNext challenge . . . \n", "utf-8" ) )
				##sleep for 1s
				time.sleep(1)
			##if guess is wrong
			else:
				## send information to client
				self.request.sendall( bytes ( "That is incorrect, format: # ## ### ... Try again!\n", "utf-8"))
				##asciiGuess set to null
				asciiGuess = ''
		#Next function
		challenge.asciiToText( self )

	##Converts the binary strings to hex
	def binToOctal( self ):
		## First decode challenge
		octal = '0o106 0o114 0o101 0o107 0o173 0o65 0o64 0o65 0o146 0o62 0o67 0o64 0o70 0o60 0o64 0o175' 
		##correct used to break out of while loop
		correct = 0
		##Stores the guess
		octalGuess = ''
		##Tells user to convert from hex to bin
		self.request.sendall( bytes ( "Convert the binary into octal!\n", "utf-8" ) )

		##while correct does not equal 1
		while correct != 1:
			##Save the client guess into binGuess
			octalGuess = self.request.recv(1024).strip()
			octalGuess = octalGuess.decode( "utf-8" )
			## If guess is equal to answer
			if octal == octalGuess:
				##Change correct to 1
				correct = 1
				##send that the answer is correct
				self.request.sendall( bytes ( "That is correct!\nNext challenge . . .\n", "utf-8" ) )
				##sleep for 1s
				time.sleep(1)
			##If guess is wrong
			else:
				##Send format and incorrect
				self.request.sendall( bytes ( "That is incorrect, format: 0o 0o 0o ... Try again.\n", "utf-8"))
				##sets binGuess to null
				octalGuess = ''
		##sends to next function
		challenge.octalToAscii( self )
		
	##Convert the octal string into hex pass in self obj
	def hexToBin ( self ):
		##correct used to break out of while loop
		correct = 0
		binary = '0b1000110 0b1001100 0b1000001 0b1000111 0b1111011 0b110101 0b110100 0b110101 0b1100110 0b110010 0b110111 0b110100 0b111000 0b110000 0b110100 0b1111101'
		##string to store users guess
		binGuess = ''
		##Proper answer (Remove the 0x?)
		hexi = '0x46 0x4c 0x41 0x47 0x7b 0x35 0x34 0x35 0x66 0x32 0x37 0x34 0x38 0x30 0x34 0x7d' 
		self.request.sendall( bytes ( "Convert the hex into binary: " + hexi + "\n", "utf-8" ) )
		##while loop to prompt user 
		while correct != 1: 
			##Receive a client side input 
			binGuess = self.request.recv(1024).strip()
			binGuess = binGuess.decode( "utf-8" )
			## If the guess string is equal to the hex string
			if binary == binGuess:
				##set correct to 1
				correct = 1
				##Sends the information to the user
				self.request.sendall( bytes ("That is correct!\nNext challenge...\n", "utf-8") ) 
				##Sleep for 1
				time.sleep ( 1 )
			##was not a correct guess
			else:
				##Send incorrect with format of how to send (could remove 0x**)
				self.request.sendall( bytes ( "That is incorrect, format: 0b 0b 0b ... Try again.\n", "utf-8"))
				##Sets the guess to null again
				binGuess = ''
		##Go to the next function
		challenge.binToOctal( self )

##Allows for passing to the first challenge in the challengers own thread/socket combination.
class TCPSocketHandler( socketserver.BaseRequestHandler ):
	def handle ( self ):
		challenge.hexToBin( self )

class SimpleServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
	## Using CTRL+C will kill all threads
	daemon_threads = True
	allow_reuse_address = True
	
	## Takes the server addres, the self obj, and tcp handler and creates a conenction
	def __init__(self, server_address, TCPSocketHandler):
		socketserver.TCPServer.__init__(self, server_address, TCPSocketHandler)

if __name__ == "__main__":

	HOST, PORT = sys.argv[1], int(sys.argv[2])
	##Creates the server for multiple users
	server = SimpleServer((HOST, PORT), TCPSocketHandler)
	try:
		server.serve_forever()
	except KeyboardInterrupt:
		sys.exit(0)
